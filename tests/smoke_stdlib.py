"""Dependency-light tests runnable with Python plus httpx and psutil."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from hamamomin.storage import Memory
from hamamomin.security import Guard, Denied
from hamamomin.coding import CodingAgent
from hamamomin.tools import Tools
from hamamomin.intents import intent

class Smoke(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.memory=Memory(self.root/'data');self.guard=Guard(self.root/'projects',self.memory,lambda a,d:True)
        self.coding=CodingAgent(self.guard,Mock())
    def tearDown(self):self.tmp.cleanup()
    def test_memory(self):
        self.memory.add('user','سڵاو');self.memory.set('rtl',True)
        self.memory.preference('language','ckb');self.memory.event('test','ok')
        other=Memory(self.memory.root)
        self.assertEqual(other.history()[0]['content'],'سڵاو')
        self.assertTrue(other.get('rtl'));self.assertEqual(other.preferences()['language'],'ckb')
        other.edit_message(1,'new');self.assertEqual(other.history()[0]['content'],'new')
        self.assertEqual(len(other.export()['events']),1)
        other.clear();self.assertEqual(other.history(),[])
    def test_paths(self):
        for value in ['../escape','/etc/passwd','CON','NUL.txt','x/a:stream']:
            with self.subTest(value=value),self.assertRaises(Denied):self.guard.path(value)
    @unittest.skipIf(os.name == 'nt', 'Symlink creation may require developer mode')
    def test_symlink(self):
        outside=self.root/'outside';outside.mkdir();(self.guard.workspace/'link').symlink_to(outside)
        with self.assertRaises(Denied):self.guard.path('link/file')
    def test_permission(self):
        with self.assertRaises(Denied):self.guard.approve('open','app',desktop=True)
        self.guard.confirm=lambda a,d:False
        with self.assertRaises(Denied):self.guard.approve('send','data')
    def test_stop(self):
        self.guard.stopped.set()
        with self.assertRaises(Denied):self.guard.path('file')
    def test_generate(self):
        self.coding.generate('my-site','Kurdish shop')
        folder=self.guard.workspace/'my-site'
        self.assertTrue((folder/'src/main.tsx').is_file())
        self.assertEqual(len([p for p in folder.rglob('*') if p.is_file()]),8)
        with self.assertRaises(FileExistsError):self.coding.generate('my-site','overwrite')
    def test_manifest_paths(self):
        for value in ['../outside','/tmp/unsafe','C:/evil','a/../../escape','a\\b','CON']:
            self.coding.llm.complete.return_value=json.dumps({'files':{value:'bad'}})
            with self.subTest(value=value),self.assertRaises((Denied,ValueError)):self.coding.generate('safe','brief',True)
        self.assertFalse((self.guard.workspace/'safe').exists())
    def test_edit(self):
        self.guard.path('code.py').write_text('def bad(:')
        self.assertIn('Line 1',self.coding.lint_python('code.py'))
        self.coding.edit('code.py','x=1');self.assertIn('valid',self.coding.lint_python('code.py'))
        self.guard.confirm=lambda a,d:False
        with self.assertRaises(Denied):self.coding.edit('code.py','x=2')
        self.assertEqual(self.coding.read('code.py'),'x=1')
    def test_command_allowlist(self):
        t=Tools(self.guard)
        with self.assertRaises(Denied):t.command('rm -rf','anything')
        with self.assertRaises(Denied):t.website('file:///etc/passwd')
    def test_subprocess(self):
        (self.guard.workspace/'project').mkdir();proc=Mock();proc.stdout=iter(['hello\n']);proc.wait.return_value=0;proc.poll.return_value=0
        with patch('hamamomin.tools.shutil.which',return_value='/usr/bin/git'),patch('hamamomin.tools.subprocess.Popen',return_value=proc) as launch:
            self.assertIn('exit code 0',Tools(self.guard).command('git-status','project'))
            self.assertFalse(launch.call_args.kwargs['shell'])
    def test_intents(self):
        self.assertEqual(intent('حەمەومین VS Code بکەرەوە'),('launch','vscode'))
        self.assertEqual(intent('حەمەومین وێبسایتی فرۆشتنم بۆ دروست بکە')[0],'studio')
    def test_model_denial(self):
        from hamamomin.llm import LLM
        self.guard.confirm=lambda a,d:False
        with patch('httpx.Client.post') as post:
            with self.assertRaises(Denied):LLM(self.memory,self.guard).complete([])
            post.assert_not_called()
    def test_model_response(self):
        from hamamomin.llm import LLM
        self.memory.set('model_enabled',True)
        response=Mock();response.json.return_value={'choices':[{'message':{'content':'سڵاو'}}]}
        with patch('hamamomin.llm.Secrets.get',return_value='fake'),patch('httpx.Client.post',return_value=response):
            self.assertEqual(LLM(self.memory,self.guard).chat('hello'),'سڵاو')
    def test_voice_wake(self):
        from hamamomin.speech import wake_match
        self.assertTrue(wake_match('Sheikh Hamamomin hello'))
        self.assertTrue(wake_match('حەمەومین چۆنی'))
        self.assertFalse(wake_match('hello'))

if __name__=='__main__':unittest.main(verbosity=2)
