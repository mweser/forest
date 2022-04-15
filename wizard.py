import asyncio
import os
import random
import shutil
import subprocess
from contextlib import redirect_stdout
from email.policy import default
from fileinput import filename
from functools import partial
from random import choice
from statistics import mode
from threading import Event
from time import sleep
from tkinter import W
from typing import Iterable, cast
from urllib.request import urlopen

import rich
from InquirerPy import base, inquirer, prompt, prompt_async, validator
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.prompt import Prompt, Confirm
from rich.text import Text


progress = Progress(
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
)

# to do:
# classes
# prune dependencies, make things less verbose
# make stubs do something


tree = open("tree").read()
rdme = open("README.md").read()

#rich 
style = "green"
console = Console()
tasks = [f"task {n}" for n in range(1, 11)]

console.print(tree, style=style)

def main():
    menu = inquirer.select(
        message="Welcome to the forest setup wizard.",
        choices=[
            Choice(value=FullerService.deploy, name="deploy.sh"),
            Choice(value=FullerService.deploy_fly_service, name="Deploy Full Service"),  # to be moved
            Choice(value=settings, name="Get Started / Change Settings"),
            Choice(value=Utils.do_docs, name="Read documentation"),
            Choice(value=Sys.do_update, name="Update from Git"),
            Choice(value=do_exit, name="Exit"),
        ],
        default=None,
    ).execute()
    menu()


def settings():
    pref = inquirer.select(
        message="What would you like to do?",
        choices=[
            Choice(value=Templates.do_newbot, name="Start a new bot from a template"),
            Choice(value=SecretAgent.do_number, name="Set bot number"),
            Choice(value=SecretAgent.set_admin, name="Set admin number"),
            Choice(value=do_auxin, name="Switch to Auxin"),
            Choice(value=SecretAgent.do_signalcli, name="Switch to Signal-Cli"),
            Choice(value=Utils.do_deps, name="Install / Check Dependencies"),
        ],
        default=None,
    ).execute()
    pref()


def do_auxin():
    auxins = inquirer.select(
        message="Do you have auxin already?",
        choices=[
            Choice(
                value=fetch_auxin,
                name="Download and set up Auxin",
                enabled=True,
            ),
            Choice(
                value=switch_auxin,
                name="I have auxin, just change the parameter in 'dev_secrets'",
            ),
        ],
    ).execute()

    auxins()



class SecretAgent:
    def parse_secrets(secrets: str) -> dict[str, str]:
        pairs = [
            line.strip().split("=", 1)
            for line in secrets.split("\n")
            if line and not line.startswith("#")
        ]
        can_be_a_dict = cast(list[tuple[str, str]], pairs)
        return dict(can_be_a_dict)


    def change_secrets(new_values: dict[str, str], **kwargs: str) -> None:
        env = os.environ.get("ENV", "dev")
        secrets = SecretAgent.parse_secrets(open(f"{env}_secrets").read())
        # py3.9 introduced dict unions
        changed = secrets | new_values | kwargs
        open(f"{env}_secrets", "w+").write(
            "\n".join(f"{k}={v}" for k, v in changed.items())
        )


    def do_number():
        NUMBER = Prompt.ask(
            "Please enter your bot's phone number in international format, e.x: +19991238458"
        )
        SecretAgent.change_secrets({"BOT_NUMBER": NUMBER})


    def set_admin() -> None:
        SecretAgent.change_secrets(
            {
                "ADMIN": Prompt.ask(
                    "Please enter your phone number in international format, e.x: +19991238458"
                )
            }
        )

    def switch_auxin():
        if Confirm.ask("Would you like to switch to Auxin?"):
            SecretAgent.change_secrets({"SIGNAL": "auxin"})

    def do_secret_signalcli():
        if Confirm.ask("Would you like to switch to Signal-CLI?"):
            SecretAgent.change_secrets({"SIGNAL": "signal-cli"})




class Sys:
    def do_rust():
        with console.status("[bold green]Setting up rust 'sh rust.sh'...") as status:
            while tasks:
                task = tasks.pop(0)
                get_rust()
                os.system("sh rust.sh")


    def get_rust():
        return subprocess.run(
            "curl -o rust.sh --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs",
            shell=True,
        )


    def do_update():
        with console.status("[bold green]git pull") as status:
            while tasks:
                return os.system("git pull")

    def do_deps():
        os.system("sh setup.sh")



    # task1 = progress.add_task("Downloading...")
    # v = "0.10.3"
    # DownLoader.copy_url(
    #    task1,
    #    url=f"https://github.com/AsamK/signal-cli/releases/download/v{v}/signal-cli-{v}-Linux.tar.gz",
    #    path="./signal-cli.tar.gz",
    # )
    # with console.status("[bold green]unzipping..") as status:
    #    task2 = progress.add_task(
    #        "unzip",
    #    )
    #    do_unzip_signal(archive="signal-cli.tar.gz")


class Utils:
    def do_docs():
        md = Markdown(rdme)
        console.print(md)
        hint = Text()
        hint.append(
            "\nScroll up to read from the beginning!", style="bold green"
        )  # probably a better solution then this?
        console.print(hint)

    def do_unzip(archive):
        os.system("tar -xvf {}".format(archive))

    def fetch_captcha():
        # https://nightly.link/mobilecoinofficial/auxin/workflows/actions/main/auxin-cli.zip
        progress.add_task("Downloading captcha helper")
        DownLoader.copy_url( #generic this
            task1,
            url=f"https://gitlab.com/api/v4/projects/27947268/jobs/artifacts/main/raw/signal-captcha-helper?job=build%3Aamd64",
            path="./signal-captcha",
        )
        subprocess.run(
            "chmod +x signal-captcha",
            shell=True,
        )
        captcha = subprocess.run("./signal-captcha", capture_output=True)
        # redirect to forest contact, prompt for a number, register
        # prompt for code/redirect to forest contact, verify, upload upload
        # see https://github.com/forestcontact/go_ham/blob/main/register.py
        # though most of that is replaced by redirecting to forest contact




class Templates:
    def do_hellobot():
        shutil.copyfile("./sample_bots/hellobot.py", "bot.py")
        return "Okay, your brand new bot template is in your Forest directory!"

    def do_newbot():
        newbot = inquirer.select(
            message="What template would you like to start with?",
            choices=[
                Choice(value=Templates.do_hellobot, name="HelloBot"),
            ],
        ).execute()
        print(newbot())


def do_exit():
    exit()


# what needs this?
done_event = Event()


def handle_sigint(signum, frame):
    done_event.set()


class FullerService:
    def deploy():
        os.system("deploy.sh")

    def test_fs():
        return "test"

    def deploy_fly_service():
        os.system("./fullerservice/create_app.sh")

class DownLoader:
    def fetch_auxin():
        # https://nightly.link/mobilecoinofficial/auxin/workflows/actions/main/auxin-cli.zip
        Utils.task1 = progress.add_task("Downloading...")
        v = "0.10.3"
        DownLoader.copy_url(
            Utils.task1,
            url=f"https://nightly.link/mobilecoinofficial/auxin/workflows/actions/main/auxin-cli.zip",
            path="./auxin.zip",
        )
        with console.status("[bold green]unzipping..") as status:
            task2 = progress.add_task(
                "unzip",
            )
            Utils.do_unzip(archive="auxin.zip")

        # os.system("git clone https://github.com/mobilecoinofficial/auxin.git")
        # os.system("rustup default nightly")
    
    def copy_url(task_id: 1, url: str, path: str) -> None:
        progress.console.log(f"Requesting {url}")
        response = urlopen(url)
        # This will break if the response doesn't contain content length
        progress.update(task_id, total=int(response.info()["Content-length"]))
        with open(path, "wb") as dest_file:
            progress.start_task(task_id)
            for data in iter(partial(response.read, 32768), b""):
                dest_file.write(data)
                progress.update(task_id, advance=len(data))
                if done_event.is_set():
                    return
        progress.console.log(f"Downloaded {path}")

    def download(urls: Iterable[str], dest_dir: str):
        with progress:
            with ThreadPoolExecutor(max_workers=4) as pool:
                for url in urls:
                    filename = url.split("/")[-1]
                    dest_path = os.path.join(dest_dir, filename)
                    task_id = progress.add_task(
                        "download", filename=filename, start=False
                    )
                    pool.submit(DownLoader.copy_url, task_id, url, dest_path)


if __name__ == "__main__":
    main()
