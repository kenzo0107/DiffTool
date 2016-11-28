#!/usr/bin/python
# coding: UTF-8

# sample:
# python diffrelo.py -t hoge -re /var/www/html -lo ~/go/src/github.com/hoge -f file.list

import sys
import os.path
import commands
import argparse

if __name__ == "__main__":

    def is_exist_remotefile(remote_hostname, remote_path):
        '''check a file exist on remote server'''
        cmd = 'ssh %s "ls %s" 2>/dev/null' % (remote_hostname, remote_path)
        r = commands.getoutput( cmd )
        p = len(remote_path)
        t= r[0:p]

        if t == remote_path:
            return True
        else:
            return False

    def get_sha1sum_remotefile(remote_hostname, remote_path):
        '''get sha1sum of file on remote server'''
        remote_dir  = os.path.dirname( os.path.abspath( remote_path ) )
        remote_file = os.path.basename(remote_path)

        cmd = 'ssh %s "cd %s;echo %s | sha1sum" 2>/dev/null' % (remote_hostname, remote_dir, remote_file)
        r = commands.getoutput( cmd )
        r = r.rstrip()
        return r

    def download_remotefile(remote_hostname, remote_path, dest='.'):
        '''download with sha1sum check'''
        remote_dir  = os.path.dirname( os.path.abspath( remote_path ) )
        remote_file = os.path.basename(remote_path)

        remote_sha1sum = get_sha1sum_remotefile(remote_hostname, remote_path)

        cmd = 'scp %s:%s %s' % (remote_hostname, remote_path, dest)
        r = commands.getoutput( cmd )

        # check sha1sum of download file
        cmd = 'cd .;echo %s | sha1sum '%( remote_file )
        r  = commands.getoutput( cmd )
        local_sha1sum = r.rstrip()

        if remote_sha1sum <> local_sha1sum:
            print '[Error] sha1sum check - mismatch! Download failed.  Please execute again. [%s]' %(remote_path)
            return False

        return True

    def delete_prefix_slash(path):
        if path[0] == '/':
            path = path[1:]
        return path

    def add_slash_to_suffix(path):
        if path[-1] != '/':
            path = '%s/' % (path)
        return path

    parser = argparse.ArgumentParser(description='do data argumentation.')
    parser.add_argument('-f',  required=True, help='Target path', metavar='compare difference paths')
    parser.add_argument('-t',  required=True, help='set host name.', metavar='Host')
    parser.add_argument('-re', required=True, help='Remote working directory.', metavar='source directory at remote server')
    parser.add_argument('-lo', required=True, help='Local working directory.', metavar='source directory at Local server')
    args = parser.parse_args()

    args.re = add_slash_to_suffix(args.re)
    args.lo = add_slash_to_suffix(args.lo)

    print '''
---------------------------------------
Remote Server (Alias): %s
remote : %s
local  : %s
list   : %s
---------------------------------------
    ''' %(args.t, args.re, args.lo, args.f)

    tmp_remote = os.path.join( os.path.dirname(__file__), './Remote/' )
    tmp_local  = os.path.join( os.path.dirname(__file__), './Local/' )

    diff_files = []
    diff_files_only_local = []
    is_remote_file = False
    is_local_file  = False

    print 'Delete tmp remote directory [%s]' % (tmp_remote)
    cmd = 'rm -rf %s*'%(tmp_remote)
    commands.getoutput( cmd )

    print 'Delete tmp local directory [%s]' %(tmp_local)
    cmd = 'rm -rf %s*'%(tmp_local)
    commands.getoutput( cmd )

    try:

        print '''
---------------------------------------
Get Remote to Local files
---------------------------------------'''

        for line in open( args.f, 'r'):

            if line is None:
                continue;

            # 末尾の改行削除
            path = line.rstrip()
            # 先頭の/削除
            path = delete_prefix_slash(path)
            print '\n%s'%(path)

            if not path is None:
                remote_path = '%s%s'%( args.re, path )
                file = os.path.basename( remote_path )

                # check exist on RemoteServer
                if is_exist_remotefile( args.t, remote_path ):

                    is_remote_file = True

                    # Download File.
                    if download_remotefile( args.t, remote_path ) is False:
                        sys.exit(1)

                    local_path  = '%s%s'%( tmp_remote, path )
                    local_dir   = os.path.dirname( os.path.abspath( local_path ) )

                    # if local_dirs not exit, create local_dir.
                    if not os.path.isdir( local_dir ):
                        cmd = 'mkdir -p %s'%( local_dir )
                        commands.getoutput( cmd )

                    # mv file to local_dir
                    cmd = 'mv %s %s/'%( file, local_dir )
                    commands.getoutput( cmd )
                    # print '[Remote] %s \n---> [Local] %s'%( remote_path, local_path )
                    print '[Remote Server] ---> [Local:%s]' % (tmp_remote)
                else:
                    is_remote_file = False
                    print '[Remote Server] No such file.\n'

                # local workspace
                workspace_path =  '%s%s'%( args.lo, path )
                if os.path.exists( workspace_path ):
                    is_local_file = True

                    workspace_save_dir = os.path.dirname( os.path.abspath( '%s%s'%( tmp_local, path ) ) )

                    if not os.path.isdir( workspace_save_dir ):
                        cmd = 'mkdir -p %s'%( workspace_save_dir )
                        res = commands.getoutput( cmd )

                    cmd = 'cp %s %s'%( workspace_path, workspace_save_dir )
                    commands.getoutput( cmd )
                    # print '[WorkSpace] %s \n---> [Upfile] %s/%s \n'%( workspace_path, workspace_save_dir, file )
                    print '[Local workspace] ---> [Local:%s]' % (tmp_local)
                else:
                    is_local_file = False
                    print '[Local Server] No such file. Please Check [%s] !! \n'%( args.f )

                if is_remote_file and is_local_file:
                    cmd = 'diff --strip-trailing-cr -r %s%s %s%s | egrep "<|>" | wc -l | tr -d " "'%( tmp_remote, path, tmp_local, path )
                    res = commands.getoutput( cmd )

                    if int(res) > 0:
                        diff_files.append(path)
                elif is_remote_file == False and is_local_file:
                    diff_files_only_local.append(path)

        print '''
--------------------------------------
Difference between LOCAL & REMOTE
--------------------------------------'''
        if len(diff_files) == 0 and len(diff_files_only_local) == 0:
            print "No difference ! Merged !"
        else:
            for l in diff_files:
                print l
            print '''
--------------------------------------
New Files
--------------------------------------
'''
            for l in diff_files_only_local:
                print l

        print 'Finish ! (^-^)/Bye!'

    except ValueError:
        print 'Error occured. Please execute again.'
        sys.exit(1)
