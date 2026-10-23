"""Conservative local routing. Model output never becomes executable commands."""

def intent(text):
    t=text.casefold()
    opening=any(word in t for word in ('open','launch','بکەرەوە','افتح'))
    if opening:
        for app, names in {'vscode':('vs code','vscode','visual studio code'), 'chrome':('chrome','کرۆم'), 'notepad':('notepad','نۆتپاد'), 'explorer':('file explorer','فایل')}.items():
            if any(name in t for name in names):return ('launch',app)
    if any(word in t for word in ('website','وێبسایت','موقع')) and any(word in t for word in ('build','create','دروست','أنشئ','انشئ')):
        return ('studio',text)
    return ('chat',text)
