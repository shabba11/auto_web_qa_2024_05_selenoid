import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.chrome.service import Service


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--executor", action="store", default="127.0.0.1")
    parser.addoption("--mobile", action="store_true")
    parser.addoption("--vnc", action="store_true")
    parser.addoption("--logs", action="store_true")
    parser.addoption("--video", action="store_true")
    parser.addoption("--bv")
    parser.addoption("--local", default=True)


@pytest.fixture
def browser(request):
    local = request.config.getoption("--local")
    browser = request.config.getoption("--browser")
    executor = request.config.getoption("--executor")
    vnc = request.config.getoption("--vnc")
    version = request.config.getoption("--bv")
    logs = request.config.getoption("--logs")
    video = request.config.getoption("--video")
    mobile = request.config.getoption("--mobile")

    executor_url = f"http://{executor}:4444/wd/hub"

    if browser == "chrome":
        options = ChromeOptions()
        service = Service()
        if local:
            driver = webdriver.Chrome(service=service)
    elif browser == "firefox":
        options = FirefoxOptions()
        if local:
            driver = webdriver.Firefox()
    elif browser == "safari":
        options = SafariOptions()
        if local:
            driver = webdriver.Safari()
    else:
        raise Exception("Driver not supported")

    caps = {
        "browserName": browser,
        "browserVersion": version,
        "selenoid:options": {
            "enableVNC": vnc,
            "name": request.node.name,
            "screenResolution": "1280x2000",
            "enableLog": logs,
            "timeZone": "Europe/Moscow",
            "env": ["LANG=ru_RU.UTF-8", "LANGUAGE=ru:en", "LC_ALL=ru_RU.UTF-8"]
        },
        "acceptInsecureCerts": True,
    }

    for k, v in caps.items():
        options.set_capability(k, v)

    if not local:
        driver = webdriver.Remote(
            command_executor=executor_url,
            options=options
        )

    if not mobile:
        driver.maximize_window()

    def finalizer():
        driver.quit()

    request.addfinalizer(finalizer)
    return driver
