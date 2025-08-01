# main.py
import imgui
import glfw
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer
import numpy as np
from PIL import Image
import trimesh
import os
from OpenGL.GL import *
import math

from Editor.editor import Editor

def main():
    e = Editor()
    e.exec()

if __name__ == "__main__":
    main()