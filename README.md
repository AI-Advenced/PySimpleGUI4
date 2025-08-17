<p align="center">
  <img src="https://raw.githubusercontent.com/PySimpleGUI/PySimpleGUI/master/images/for_readme/Logo%20with%20text%20for%20GitHub%20Top.png" alt="User Interfaces for Humans">
</p>
This repository provides a functional, pre-license version of the **PySimpleGUI** library for developers who need a free and unrestricted solution. The official PySimpleGUI library has recently transitioned to a paid license model, leaving many developers unable to access or use the library. This backup allows you to continue using the legacy version without any license requirements.

---

## What is PySimpleGUI4?

**PySimpleGUI** is a Python library that simplifies the process of creating graphical user interfaces (GUIs). It abstracts away the complexity of underlying frameworks like Tkinter, Qt, WxPython, and Remi, offering a beginner-friendly, high-level API. With PySimpleGUI, you can build interactive desktop applications, file explorers, progress trackers, and more with minimal code.


## Key Features of PySimpleGUI:
- **Beginner-Friendly**: Intuitive syntax, ideal for developers new to GUIs.
- **Rich Component Library**: Buttons, text inputs, sliders, progress bars, tables, and more.
- **Cross-Platform**: Runs seamlessly on Windows, macOS, and Linux.
- **Dynamic Updates**: Allows real-time updates to GUI elements during execution.
- **Integration Ready**: Supports Matplotlib, OpenCV, and other libraries for advanced functionality.

---

## install
~~~bash
pip install PySimpleGUI4
~~~
## How To Use PySimpleGUI4
~~~python
import PySimpleGUI4 as sg
~~~

## What is PySimpleGUI4 Used For?

PySimpleGUI4 is widely used in:
- **Educational Projects**: Helping beginners learn GUI development.
- **Data Visualization**: Embedding interactive charts and graphs.
- **Automation Tools**: Creating simple automation utilities with user interfaces.
- **Prototyping**: Quickly designing and testing application interfaces.
- **Lightweight Desktop Apps**: Developing small-scale tools with a minimal footprint.

---

## Why Use PySimpleGUI4?

On **[specific date of license change]**, the creator of PySimpleGUI announced a transition to a paid license model. As part of this change:
1. **A license key is now required** to use any version installed via `pip`.
2. **Older, free versions of PySimpleGUI have been removed** from the PyPI repository, preventing developers from simply downgrading to a previous version.
3. Developers who rely on PySimpleGUI for personal projects, open-source software, or educational purposes are now locked out unless they pay for a license.

This repository offers a solution by providing a backup of the last free and functional version of PySimpleGUI.

---


### **6. Verify the Installation**

You can verify that the legacy version is installed correctly by running a simple PySimpleGUI script:

```python
import PySimpleGUI4 as sg
from pyguievent import PySimpleEvent

app = PySimpleEvent()


def make_main_window() -> sg.Window:
    task_list = [
        sg.Frame(
            "Tasks",
            [
                [sg.Input(key="lot", tooltip="此输入框输入后使用回车事件触发")],
                [sg.Text(key="lot_txt")],
            ],
            size=(400, 200),
        )
    ]

    status_bar = [sg.StatusBar("版本:"), sg.StatusBar("状态:")]

    layout = [task_list, status_bar]

    # 3.建窗口
    return sg.Window("测试程式窗口", layout, return_keyboard_events=True)


@app.bind_event("lot")
def on_lot(window: sg.Window, values: dict):
    lot = values["lot"]
    window["lot_txt"].update(lot)


def main():
    main_window = make_main_window()
    app.run_event(main_window)


if __name__ == "__main__":
    main()
```

Run the script to ensure that the GUI appears and functions as expected.
