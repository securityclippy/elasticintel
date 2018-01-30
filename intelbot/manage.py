#!/usr/bin/env python3

import os
import argparse
import subprocess

def  up_lambda():
    homedir = os.path.abspath(os.curdir)
    config_file = os.path.join(homedir, "lambdabot.conf")
    os.chdir("terraform/dev/lambda")
    if not os.path.isdir(".terraform"):
        print(subprocess.check_call(["terraform", "init"]))
    print(subprocess.check_call(["terraform", "apply", "-var-file", config_file]))
    os.chdir(homedir)
    return

def apply():
    homedir = os.path.abspath(os.curdir)
    config_file = os.path.join(homedir, "lambdabot.conf")
    os.chdir("terraform/dev/ssm_parameter_store")
    if not os.path.isdir(".terraform"):
        print(subprocess.check_call(["terraform", "init"]))
    print(subprocess.check_call(["terraform", "apply", "-var-file", config_file]))
    os.chdir(homedir)
    os.chdir("terraform/dev/lambda")
    if not os.path.isdir(".terraform"):
        print(subprocess.check_call(["terraform", "init"]))
    print(subprocess.check_call(["terraform", "apply", "-var-file", config_file]))
    os.chdir(homedir)
    os.chdir("terraform/dev/api_gateway")
    if not os.path.isdir(".terraform"):
        print(subprocess.check_call(["terraform", "init"]))
    print(subprocess.check_call(["terraform", "apply", "-var-file", config_file]))
    os.chdir(homedir)


def destroy():
    homedir = os.path.abspath(os.curdir)
    config_file = os.path.join(homedir, "lambdabot.conf")
    os.chdir("terraform/dev/ssm_parameter_store")
    print(subprocess.check_call(["terraform", "destroy", "-var-file", config_file, "-force"]))
    os.chdir(homedir)
    os.chdir("terraform/dev/lambda")
    print(subprocess.check_call(["terraform", "destroy", "-var-file", config_file, "-force"]))
    os.chdir(homedir)
    os.chdir("terraform/dev/api_gateway")
    print(subprocess.check_call(["terraform", "destroy", "-var-file", config_file, "-force"]))
    os.chdir(homedir)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', help='deploy lambdabot', action='store_true')
    parser.add_argument('--destroy', help='destroy lambdabot',  action='store_true')
    parser.add_argument('--lam', help='apply lambda', action='store_true')
    args = parser.parse_args()
    if args.apply:
        apply()
    if args.lam:
        up_lambda()
    if args.destroy:
        destroy()


if __name__ == '__main__':
    main()
