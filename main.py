import time
import json
from typing import Dict, List
from python_hue_v2.scene import action
from pywebostv.connection import WebOSClient
from pywebostv.controls import (
    MediaControl,
    SystemControl,
    ApplicationControl,
    SourceControl,
)
from pywebostv.discovery import discover
from pywebostv.model import Application, InputSource, AudioOutputSource


from python_hue_v2 import Hue, BridgeFinder, Scene


import os


# from gpiozero import Button

KEY_FILE = "webos_key.json"
LG_IP = "192.168.2.6"

# button_1 = Button(2)


def main():
    print("Discovering devices...")

    try:
        with open(KEY_FILE, "r") as f:
            store = json.load(f)
        print("Loaded existing pairing key")
    except FileNotFoundError:
        store = {}
        print("No existing pairing key found")
        # Create a WebOS client
        with open("webos_key.json", "r") as f:
            store = json.load(f)

    client = WebOSClient("192.168.2.6", secure=True)
    client.connect()
    for status in client.register(store):
        if status == WebOSClient.PROMPTED:
            print("Please accept the pairing request on your TV")
        elif status == WebOSClient.REGISTERED:
            print("Successfully registered!")

    # Save the pairing key for future use
    media = MediaControl(client)
    app = ApplicationControl(client)
    apps = app.list_apps(block=True)
    source = SourceControl(client)
    inputs_sources = source.list_sources(block=True)
    run = True
    while run:
        input_num = int(input("what to do"))
        match input_num:
            case 1:
                switch_tv(apps, app, "crunchyroll")
            case 2:
                switch_tv(apps, app, "youtube")
            case 3:
                switch_tv(apps, app, "hbo")
            case 4:
                switch_tv(apps, app, "kpn")
            case 5:
                switch_tv(inputs_sources, source, "nintendo")
            case 6:
                switch_tv(inputs_sources, source, "xbox")
            case 7:
                switch_tv(inputs_sources, source, "playstation")
            case 8:
                run = False
            case 9:
                media.pause(block=True)
            case 10:
                media.play(block=True)
            case 11:
                media.rewind(block=True)
            case 12:
                media.fast_forward(block=True)
            case 13:
                media.stop(block=True)


def get_instance_source(source: list[InputSource], key: str) -> InputSource | None:
    app_data = next((app for app in source if key in app["label"].lower()), None)
    return app_data


def get_instance_app(source: list[Application], key: str) -> Application | None:
    app_data = next((app for app in source if key in app["title"].lower()), None)
    return app_data


def switch_tv(
    source: list[InputSource] | list[Application],
    controller: ApplicationControl | SourceControl,
    key: str,
):
    if isinstance(controller, ApplicationControl) and isinstance(
        source[0], Application
    ):
        id = get_instance_app(source, key)
        controller.launch(id, block=True)
    elif isinstance(controller, SourceControl) and isinstance(source[0], InputSource):
        id = get_instance_source(source, key)
        controller.set_source(id, block=True)
    else:
        print("not supported")


# structure
class HueSetup:
    def __init__(self) -> None:
        self.client = Hue("192.168.2.5", "c4IgoaVg0wYRkfCufPSWIg4gtLf6dANShnnLgobG")
        scenes = self.client.scenes
        self.scenes: Dict[str, List[Scene]] = {}
        self.lights = self.client.lights
        self.groups = self.client.grouped_lights

        for scene in scenes:
            if scene.meta_data.name in self.scenes.keys():
                self.scenes[scene.meta_data.name].append(scene)
            else:
                self.scenes[scene.meta_data.name] = [scene]
        self.rooms = self.client.rooms

    def switch_scene(self, key):
        for scene in self.scenes[key]:
            scene.recall(action="active")

    def kill_all(self):
        for i in self.lights:
            i.on = False

    def switch_group(self, key: int):
        rooms_state = self.groups[key].on
        print(self.groups)
        self.groups[key].set_state(not rooms_state)



# init variables on start, get list of apps, source, and grep names of scenes and store them.
# while loop when button is pressed call the function to set the action
# TODO
# create hue functions and structure
# set up gpio functions
# auto start on starting of  pi
# monitor battery with action???
class Remote:
    def __init__(self) -> None:
        self.lg_client = self._create_lg_client()
        self.hue_client = HueSetup()
        self.media = MediaControl(self.lg_client)
        self.app = ApplicationControl(self.lg_client)
        self.apps = self.app.list_apps(block=True)
        self.source = SourceControl(self.lg_client)
        self.inputs_sources = self.source.list_sources(block=True)

    def _create_lg_client(self) -> WebOSClient:
        try:
            with open(KEY_FILE, "r") as f:
                store = json.load(f)
            print("Loaded existing pairing key")
        except FileNotFoundError:
            store = {}
            print("No existing pairing key found")
            # Create a WebOS client
            with open("webos_key.json", "r") as f:
                store = json.load(f)

        client = WebOSClient(LG_IP, secure=True)
        client.connect()
        for status in client.register(store):
            if status == WebOSClient.PROMPTED:
                print("Please accept the pairing request on your TV")
            elif status == WebOSClient.REGISTERED:
                print("Successfully registered!")
        return client

    def main_loop(self):
        run = True
        while run:
            input_num = int(input("what to do"))
            match input_num:
                case 1:
                    switch_tv(self.apps, self.app, "crunchyroll")
                case 2:
                    switch_tv(self.apps, self.app, "youtube")
                case 3:
                    switch_tv(self.apps, self.app, "hbo")
                case 4:
                    switch_tv(self.apps, self.app, "kpn")
                case 5:
                    switch_tv(self.inputs_sources, self.source, "nintendo")
                case 6:
                    switch_tv(self.inputs_sources, self.source, "xbox")
                case 7:
                    switch_tv(self.inputs_sources, self.source, "playstation")
                case 8:
                    run = False
                case 9:
                    self.media.pause(block=True)
                case 10:
                    self.media.play(block=True)
                case 11:
                    self.media.rewind(block=True)
                case 12:
                    self.media.fast_forward(block=True)
                case 13:
                    self.media.stop(block=True)
                case 14:
                    self.hue_client.kill_all()
                case 15:
                    self.hue_client.switch_group(4)
                case 16:
                    self.hue_client.switch_group(1)
                case 17:
                    self.hue_client.switch_group(2)
                case 18:
                    self.hue_client.switch_group(3)
                case 19:
                    self.hue_client.switch_scene("Lezen")
                case 20:
                    self.hue_client.switch_scene("Consentrere")
                case 21:
                    self.hue_client.switch_scene("Romantice")
                case 22:
                    self.hue_client.switch_scene("Film")


if __name__ == "__main__":
    remote = Remote()
    print(remote.hue_client.rooms)
    remote.main_loop()
