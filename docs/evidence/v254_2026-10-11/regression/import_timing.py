import json, os, time
def run(b, port, rt, v24):
    out = []
    for i in range(int(os.environ.get('N', '15'))):
        g = rt.Game(b, port, 'index', seed=3, manual=True)
        g.click('[data-act=settings]')
        with g.page.expect_file_chooser() as fc:
            g.click('[data-act=import]')
        t0 = time.time(); fc.value.set_files(os.path.join(rt.FIXTURES, 'v16_backup_file.json'))
        while not g.ev("!!(typeof pendingImport!=='undefined'&&pendingImport)") and time.time() - t0 < 5: pass
        out.append(round((time.time() - t0) * 1000)); g.close()
    out.sort(); print('ms from set_files until the game has the file:', out, 'median', out[len(out)//2], 'max', out[-1])
