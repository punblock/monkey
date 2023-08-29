
from __future__ import print_function

import os
import sys
import shutil

def not_null(*xs):
    for x in xs:
        if x is not None:
            return x
    return None
    
class MonkeyParseArgument:
        
    def __init__(self):
        self._options = [
        ]
        self._next = 0
    
    def set_argv(self, argc, argv):
        self._argv = argc
        self._argv = argv
        
    def Main(self):
        return self.runNextDirective()
    
    def runNextDirective(self):
        rCode = getattr(self, self.directive().replace('-', '_'))()
        if rCode == 0:
            if not self.eof():
                raise Exception("No all input consum")
        else:
            print("Error;")
        return rCode
    
    def directive(self):
        while not self.eof():
            load = self.peekToken()
            if load not in Monkey.DirectiveKey:
                if load.startswith('--') \
                    and (load[2:].replace('-', '_') in Monkey.DirectiveKey):
                    return load[2:]
                self.loadToken()
                continue
            else:
                return load
        raise Exception('except for a directive but end of argv')
    
    def peekNextDirective(self):
        while not self.eof():
            self.peek()
            if self.peekIsDirective():
                break
            
    def peekOption(self):
        options = [[None, []]]
        optionKey, rvals = options[0]
        index = self._next
        while index < len(self._argv):
            if self._argv[index].startswith('--'):
                xs = self._argv[index][2:]
                if xs in Monkey.DirectiveKey:
                    break
                optionKey = self._argv[index]
                rvals = []
                options.append([optionKey, rvals])
                index = index + 1
            else:
                token = self._argv[index]
                rvals.append(token)
                index = index + 1
        self._next = index
        return options
    
    def resolve_option(self, key):
        while not self.eof():
            load = self.loadToken()
            if load != key:
                continue
            return load
        raise Exception('unexcpet end of argv')
    
    def eof(self):
        return self._next >= len(self._argv)
    
    def peek(self):
        if self._next < len(self._argv):
            self._next = self._next + 1
        return
    
    def peekToken(self):
        if self._next < len(self._argv):
            return self._argv[self._next]
        return None
    
    def peekIsDirective(self):
        return self.peekToken() in self.directiveKey
    
    def peekIsOption(self):
        return self.peekToken().startswith('--')
    
    def loadToken(self):
        token = self.peekToken()
        self.peek()
        number = self.praseNumber(token)
        if number is not None:
            return number
        return token
    
    def praseNumber(self, x):
        try:
            if '.' in x:
                try:
                    x = float(x)
                except:
                    return None
                return x
        except:
            return None
        try:
            x = int(x)
        except:
            return None
        return x
    
    def collect_option(self):
        return dict(self._options)
    
    def add_option(self, key, value):
        if key == None:
            key = 'Monkey'
        for c, vals in self._options:
            if c == key:
                vals.append(value)
                return
        self._options.append([key, [value]])
        
    def forget_option(self):
        self._options = [
        ]
        
class MonkeyBuildPromptBox:
    
    def __init__(self):
        self._prompt = []
        self._filter = 0
        self._subscribers = []
        
    def subscriber(self, f, stage):
        self._subscribers.append([f, stage])
        
    def set_filter(self, filter_):
        self._filter = int(filter_)
        
    def resolve_visibility(self, stageS, stageN):
        if '*' in stageS:
            return True
        for a in stageN:
            if a in stageS:
                return True
        return False
        
    def notify(self, stage, prompt, level=5):
        if level > self._filter:
            return
        self._prompt.append([stage, prompt, level])
        for f, stageS in self._subscribers:
            if self.resolve_visibility(stageS, stage):
                f.MonkeyPromptBoxRecv(stage, prompt, level)
                
    def flush(self):
        self._prompt = []
        
class MonkeyScreenPrinter:
    
    def MonkeyPromptBoxRecv(self, stage, prompt, level):
        print(prompt, end='')
    
class Monkey(MonkeyParseArgument):
    
    DirectiveKey = [
        'build_project'
    ]
    
    def __init__(self):
        MonkeyParseArgument.__init__(self)
        self._pbox = MonkeyBuildPromptBox()
        self._pbox.set_filter(5)
        self._pbox.subscriber(MonkeyScreenPrinter(), '12XZ')
        
    def resolve_dir(self, goaldir, filter_=None):
        count = 0
        buf = []
        for point, dirs, files in os.walk(goaldir):
            for f in files:
                ap = os.path.join(point, f)
                rap = os.path.relpath(ap, goaldir)
                aap = os.path.abspath(ap)
                if (filter_ is not None) and (not filter_(count, rap, aap)):
                    continue
                count = count + 1
                buf.append([count, rap, aap])
        return buf
    
    def search_entry(self, option, key):
        for xs, rvals in option:
            if key == xs:
                if len(rvals) == 0:
                    return [xs]
                return rvals
        return None
    
    def search_entry_first(self, option, key):
        rvals = self.search_entry(option, key)
        if rvals is not None:
            return rvals[0]
    
    def resolve_abspath(self, path, makeNew=None):
        if path is None:
            raise Exception("except a file or dir path")            
        ap = os.path.abspath(path)
        if not os.path.exists(ap):
            if makeNew is True:
                os.makedirs(ap)
                return ap
            raise Exception("No such file or dir exists; %s" % path)
        return ap
    
    def parse_dir(self, option):
        if self.search_entry_first(option, '--goal'):
            goal_path = self.search_entry_first(option, '--goal')
            src_path = os.path.join(goal_path, 'src')
            build_path = os.path.join(goal_path, 'build')
            dist_path = os.path.join(goal_path, 'dist')
        else:
            src_path = build_path = dist_path = None
        src_path = self.resolve_abspath(not_null(
                self.search_entry_first(option, '--src'),
                src_path))
        build_path = self.resolve_abspath(not_null(
                self.search_entry_first(option, '--build'),
                build_path,
                os.path.join(src_path, '../build') if src_path is not None else None),
                makeNew=True)
        dist_path = self.resolve_abspath(not_null(
                self.search_entry_first(option, '--dist'),
                dist_path,
                os.path.join(src_path, '../dist') if src_path is not None else None,
                os.path.join(build_path, '../dist') if build_path is not None else None),
                makeNew=True)
        return (src_path, build_path, dist_path)
    
    def is_newer(self, aap, bap):
        try:
            if os.stat(aap).st_mtime > os.stat(bap).st_mtime:
                return True
            else:
                return False
        except:
            return False
        return True
    
    def _resolve_assemble_filename(self, bap):
        if bap.endswith('.c'):
            return bap[:-2] + '.mk.as.o'
        raise Exception("Resolve assemble filename error")
    
    def _resolve_dist_filename(self, bap):
        if bap.endswith('.mk.dist.out'):
            return bap[:-12] + '.out'
        raise Exception("Resolve assemble filename error")
    
    def _c_filter(self, count, rap, aap):
        return rap.endswith('.c')
    
    def _assemble_object_filter(self, count, rap, aap):
        return rap.endswith('.mk.as.o')
    
    def _dist_object_filter(self, count, rap, aap):
        return rap.endswith('.mk.dist.out')        
    
    def _build_assemble(self, count, aap, bap):
        cmd = 'gcc -c %s -o %s' % (aap, bap)
        self._pbox.notify('1', 'Cmd: %s ' % cmd, 5)
        try:
            rCode = os.system(cmd)
        except Exception as e:
            self._pbox.notify('1', ' errore; %s\n', 5)
            return False
        self._pbox.notify('1', 'rcode=%s\n' % rCode, 5)
        return True
    
    def _build_assemble_dir(self, src_path, build_path):
        targetlist = self.resolve_dir(src_path, self._c_filter)
        error = 0
        update = 0
        for count, rap, aap in targetlist:
            bap = self._resolve_assemble_filename(os.path.abspath(os.path.join(build_path, rap)))
            if self.is_newer(bap, aap):
                continue
            update = update + 1
            self._pbox.notify('1', 'Build_assemble[%d]: %s -> %s\n' % (count, aap, bap), 5)
            if not os.path.exists(os.path.dirname(bap)) : 
                os.makedirs(os.path.dirname(bap))
            if self._build_assemble(count, aap, bap) is not True:
                error = error + 1
        if update > 0:
            self._pbox.notify('1', 'Build_assemble done. File: %s ; Error: %s \n' % (len(targetlist), error), 5)
        else:
            self._pbox.notify('X', 'Build_assemble done. File: %s ; Error: %s \n' % (len(targetlist), error), 6)           
        return 1 if (error > 0) else 0
            
    def _build_main_dir(self, src_path, build_path):
        targetlist = self.resolve_dir(build_path, self._assemble_object_filter)
        buf = ['gcc']
        isNewer = False
        bap = os.path.join(build_path, 'a.mk.dist.out')
        for count, rap, aap in targetlist:
            if not self.is_newer(bap, aap):
                isNewer = True
            buf.append(aap)
        if not isNewer:
            self._pbox.notify('X', 'Build_main: Not Update\n', 6)
            return 0
        buf.append('-o')
        buf.append(bap)
        self._pbox.notify('2', 'Build_main: Update\n', 5)
        cmd = ' '.join(buf)
        self._pbox.notify('2', 'Cmd: %s ' % cmd, 5)
        rCode = os.system(cmd)
        self._pbox.notify('2', 'rcode=%s\n' % rCode, 5)
        return 0

    def _build_dist_dir(self, src_path, build_path, dist_path):
        targetlist = self.resolve_dir(build_path, self._dist_object_filter)
        error = 0
        update = 0
        for count, rap, aap in targetlist:
            bap = self._resolve_dist_filename(os.path.abspath(os.path.join(dist_path, rap)))
            if self.is_newer(bap, aap):
                continue
            update = update + 1
            self._pbox.notify('Z', 'Build_dist[%d]: %s -> %s' % (count, aap, bap), 5)
            try:
                shutil.copy(aap, bap)
            except Exception as e:
                self._pbox.notify(' error; %s' % e)
                error = error + 1
                continue
            self._pbox.notify('Z', ' Done\n')
        if update > 0:
            self._pbox.notify('Z', 'Build_dist done. File: %s ; Error: %s\n' % (len(targetlist), error), 5)
        else:
            self._pbox.notify('X', 'Build_dist done. File: %s ; Error: %s\n' % (len(targetlist), error), 6)            
        return 1 if (error > 0) else 0
    
    def _run(self, dist_path):
        bap = os.path.join(dist_path, 'a.out')
        os.system('%s &' % bap)
        
    def build_project(self):
        self.loadToken()
        option = self.peekOption()
        src_path, build_path, dist_path = self.parse_dir(option)        
        if self.search_entry_first(option, '--clear-screen'):
            os.system('clean')
        self._pbox.notify('X', '[** Build Project **]\n', 5)
        self._pbox.notify('X', 'Build_for_path: %s, %s, %s\n' % (src_path, build_path, dist_path), 5)
        error = self._build_assemble_dir(src_path, build_path)
        error = self._build_main_dir(src_path, build_path) + error
        error = self._build_dist_dir(src_path, build_path, dist_path) + error
        self._pbox.notify('X', '[** Build Project Exit **]\n', 5)
        if error > 0 :
            return 1
        if self.search_entry_first(option, '--try-run'):
            self._run(dist_path)
        return 0

if __name__ == "__main__":
    monkey = Monkey()
    monkey.set_argv(len(sys.argv), sys.argv)
    rCode = int(monkey.Main())
    exit(rCode)
