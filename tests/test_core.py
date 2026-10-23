import json
import os
from pathlib import Path
from unittest.mock import Mock
import pytest
from hamamomin.storage import Memory
from hamamomin.security import Guard, Denied
from hamamomin.coding import CodingAgent
from hamamomin.tools import Tools
from hamamomin.intents import intent

@pytest.fixture
def core(tmp_path):
    memory=Memory(tmp_path/'data')
    guard=Guard(tmp_path/'workspace',memory,lambda a,d:True)
    return memory,guard,CodingAgent(guard,Mock())

def test_memory_persistence_and_export(core):
    m,g,c=core;m.add('user','حەمەومین چۆنی؟');m.set('rtl',True);m.preference('language','ckb');m.event('task','created')
    reopened=Memory(m.root)
    assert reopened.history()[0]['content']=='حەمەومین چۆنی؟'
    assert reopened.get('rtl') is True
    assert reopened.preferences()=={'language':'ckb'}
    reopened.edit_message(1,'new');assert reopened.history()[0]['content']=='new'
    assert len(reopened.export()['events'])==1
    reopened.clear();assert reopened.history()==[];assert reopened.get('rtl') is True

@pytest.mark.parametrize('path',['../secret','/etc/passwd','CON','folder/a:stream','NUL.txt'])
def test_path_block(core,path):
    with pytest.raises(Denied):core[1].path(path)

@pytest.mark.skipif(os.name == 'nt', reason='Symlink creation may require Windows developer mode')
def test_symlink_escape(core,tmp_path):
    outside=tmp_path/'outside';outside.mkdir();(core[1].workspace/'link').symlink_to(outside,target_is_directory=True)
    with pytest.raises(Denied):core[1].path('link/file')

def test_permission_and_emergency(core):
    m,g,c=core
    with pytest.raises(Denied):g.approve('open','app',desktop=True)
    g.confirm=lambda a,d:False
    with pytest.raises(Denied):g.approve('request','data')
    g.stopped.set()
    with pytest.raises(Denied):g.path('test')

def test_generate_real_project_and_no_overwrite(core):
    m,g,c=core
    c.generate('my-site','Kurdish shop')
    root=g.workspace/'my-site'
    assert (root/'src/main.tsx').is_file()
    assert json.loads((root/'package.json').read_text())['scripts']['build']
    assert len(list(root.rglob('*')))>8
    with pytest.raises(FileExistsError):c.generate('my-site','overwrite')

@pytest.mark.parametrize('rel',['../outside','/tmp/unsafe','a/../../escape','C:/evil','a\\b','CON'])
def test_untrusted_manifest_paths(core,rel):
    m,g,c=core;c.llm.complete.return_value=json.dumps({'files':{rel:'bad'}})
    with pytest.raises((ValueError,Denied)):c.generate('safe','test',ai=True)
    assert not (g.workspace/'safe').exists()

def test_invalid_manifest_is_atomic(core):
    m,g,c=core;c.llm.complete.return_value=json.dumps({'files':{'ok.txt':'fine','other.txt':123}})
    with pytest.raises(ValueError):c.generate('safe','brief',ai=True)
    assert not (g.workspace/'safe').exists()

def test_edit_and_python_lint(core):
    m,g,c=core;p=g.path('code.py');p.write_text('def bad(:')
    assert 'Line 1' in c.lint_python('code.py')
    c.edit('code.py','x = 1');assert 'valid' in c.lint_python('code.py')
    g.confirm=lambda a,d:False
    with pytest.raises(Denied):c.edit('code.py','x=2')
    assert p.read_text()=='x = 1'

def test_tools_reject_shell_and_url(core):
    tools=Tools(core[1])
    with pytest.raises(Denied):tools.command('rm -rf','project')
    with pytest.raises(Denied):tools.website('file:///etc/passwd')
    with pytest.raises(Denied):tools.website('https://user:pass@example.com')

def test_commands_run_and_audit(core,monkeypatch):
    m,g,c=core;(g.workspace/'project').mkdir()
    proc=Mock();proc.stdout=iter(['hello\n']);proc.wait.return_value=0;proc.poll.return_value=0
    monkeypatch.setattr('hamamomin.tools.shutil.which',lambda name:'/usr/bin/'+name)
    launch=Mock(return_value=proc);monkeypatch.setattr('hamamomin.tools.subprocess.Popen',launch)
    output=[];tools=Tools(g,output.append)
    assert 'exit code 0' in tools.command('git-status','project')
    assert output==['hello']
    assert launch.call_args.kwargs['shell'] is False
    assert any(e['kind']=='command' for e in m.export()['events'])

def test_natural_intents():
    assert intent('حەمەومین VS Code بکەرەوە')==('launch','vscode')
    assert intent('Open Chrome')==('launch','chrome')
    assert intent('حەمەومین وێبسایتی فرۆشتنم بۆ دروست بکە')[0]=='studio'
    assert intent('Explain subprocess')[0]=='chat'

def test_llm_consent_blocks_request(core,monkeypatch):
    from hamamomin.llm import LLM
    m,g,c=core;g.confirm=lambda a,d:False
    post=Mock();monkeypatch.setattr('httpx.Client.post',post)
    with pytest.raises(Denied):LLM(m,g).complete([])
    post.assert_not_called()

def test_llm_adapter_and_context(core,monkeypatch):
    from hamamomin.llm import LLM
    m,g,c=core;m.set('model_enabled',True);m.add('user','old');m.preference('language','ckb')
    monkeypatch.setattr('hamamomin.llm.Secrets.get',lambda:'fake-key')
    response=Mock();response.json.return_value={'choices':[{'message':{'content':'سڵاو'}}]}
    post=Mock(return_value=response);monkeypatch.setattr('httpx.Client.post',post)
    assert LLM(m,g).chat('hello')=='سڵاو'
    messages=post.call_args.kwargs['json']['messages']
    assert messages[-1]['content']=='hello';assert messages[-2]['content']=='old'


def test_service():
    from fastapi.testclient import TestClient
    from hamamomin.service import app
    assert TestClient(app).get('/health').json()['tools_exposed'] is False


def test_sqlite_connection_releases_windows_file(core):
    import sqlite3
    with core[0].connect() as db:
        assert db.execute('SELECT 1').fetchone()[0]==1
    with pytest.raises(sqlite3.ProgrammingError):
        db.execute('SELECT 1')
    original=core[0].path
    moved=original.with_suffix('.moved')
    original.rename(moved)
    moved.rename(original)
