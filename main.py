import data
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

# no modificar
def retrieve_phone_code(driver) -> str:
    import json
    import time
    from selenium.common import WebDriverException
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.\n"
                            "Utiliza 'retrieve_phone_code' solo después de haber solicitado el código en tu aplicación.")
        return code


class UrbanRoutesPage:
    from_field = (By.CSS_SELECTOR, 'input#from')  # CSS Selector
    to_field = (By.CSS_SELECTOR, 'input#to')  # CSS Selector
    comfort_button = (By.CLASS_NAME, 'comfort-button')  # ClassName
    phone_field = (By.ID, 'phone')
    add_card_button = (By.CLASS_NAME, 'add-card')  # ClassName
    cvv_field = (By.ID, 'code')
    message_field = (By.CSS_SELECTOR, 'textarea#message')  # CSS Selector
    blanket_button = (By.ID, 'blanket')
    tissues_button = (By.CLASS_NAME, 'tissues-button')  # ClassName
    ice_cream_button = (By.ID, 'ice-cream')
    taxi_modal = (By.ID, 'taxi-modal')
    driver_info = (By.CLASS_NAME, 'driver-info')  # ClassName

    def __init__(self, driver):
        self.driver = driver

    def set_from(self, from_address):
        self.driver.find_element(*self.from_field).send_keys(from_address)

    def set_to(self, to_address):
        self.driver.find_element(*self.to_field).send_keys(to_address)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def select_comfort(self):
        self.driver.find_element(*self.comfort_button).click()

    def enter_phone_number(self, phone_number):
        self.driver.find_element(*self.phone_field).send_keys(phone_number)

    def add_credit_card(self, card_number, card_code):
        self.driver.find_element(*self.add_card_button).click()
        self.driver.find_element(By.ID, 'card-number').send_keys(card_number)
        self.driver.find_element(By.ID, 'card-code').send_keys(card_code)
        self.driver.find_element(*self.cvv_field).send_keys(Keys.TAB)
        self.driver.find_element(By.ID, 'link').click()

    def write_message_for_driver(self, message):
        self.driver.find_element(*self.message_field).send_keys(message)

    def request_blanket_and_tissues(self):
        self.driver.find_element(*self.blanket_button).click()
        self.driver.find_element(*self.tissues_button).click()

    def order_ice_cream(self, quantity):
        for _ in range(quantity):
            self.driver.find_element(*self.ice_cream_button).click()

    def wait_for_taxi_modal(self):
        WebDriverWait(self.driver, 20).until(
            expected_conditions.visibility_of_element_located(self.taxi_modal)
        )

    def wait_for_driver_info(self):
        WebDriverWait(self.driver, 20).until(
            expected_conditions.visibility_of_element_located(self.driver_info)
        )


class TestUrbanRoutes:

    driver = None

    @classmethod
    def setup_class(cls):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')

        service = Service(executable_path='/path/to/chromedriver')
        cls.driver = webdriver.Chrome(service=service, options=chrome_options)

    def test_set_route(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        address_from = data.address_from
        address_to = data.address_to
        routes_page.set_from(address_from)
        routes_page.set_to(address_to)
        assert routes_page.get_from() == address_from
        assert routes_page.get_to() == address_to

    def test_select_comfort_and_fill_phone_number(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.select_comfort()
        assert "comfort" in self.driver.find_element(*routes_page.comfort_button).get_attribute('class')  # Validación
        routes_page.enter_phone_number(data.phone_number)
        assert self.driver.find_element(*routes_page.phone_field).get_property('value') == data.phone_number

    def test_add_credit_card(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.add_credit_card(data.card_number, data.card_code)
        assert "success" in self.driver.find_element(By.ID, 'card-status').text  # Validación

    def test_message_for_driver(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.write_message_for_driver(data.message_for_driver)
        assert routes_page.driver.find_element(*routes_page.message_field).get_property('value') == data.message_for_driver

    def test_order_blanket_tissues_and_ice_cream(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.request_blanket_and_tissues()
        assert "selected" in self.driver.find_element(*routes_page.blanket_button).get_attribute('class')  # Validación
        assert "selected" in self.driver.find_element(*routes_page.tissues_button).get_attribute('class')  # Validación
        routes_page.order_ice_cream(2)
        assert int(self.driver.find_element(By.ID, 'ice-cream-counter').text) == 2  # Validación

    def test_taxi_modal_appears(self):
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.wait_for_taxi_modal()
        assert self.driver.find_element(*routes_page.taxi_modal).is_displayed()
        routes_page.wait_for_driver_info()
        assert self.driver.find_element(*routes_page.driver_info).is_displayed()

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()
