import data
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


class UrbanRoutesPage:
    # Selectores utilizando diferentes tipos
    from_field = (By.CSS_SELECTOR, 'input#from')  # CSS Selector
    to_field = (By.ID, 'to')  # ID
    comfort_button = (By.CLASS_NAME, 'comfort-button')  # ClassName
    phone_field = (By.XPATH, '//input[@id="phone"]')  # XPath
    add_card_button = (By.CLASS_NAME, 'add-card')  # ClassName
    cvv_field = (By.ID, 'code')  # ID
    message_field = (By.CSS_SELECTOR, 'textarea#message')  # CSS Selector
    blanket_button = (By.XPATH, '//button[@id="blanket"]')  # XPath
    tissues_button = (By.CLASS_NAME, 'tissues-button')  # ClassName
    ice_cream_button = (By.ID, 'ice-cream')  # ID
    taxi_modal = (By.ID, 'taxi-modal')  # ID
    driver_info = (By.XPATH, '//div[contains(@class, "driver-info")]')  # XPath

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

        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def test_complete_taxi_order_process(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)

        # Paso 1: Configurar direcciones
        address_from = data.address_from
        address_to = data.address_to
        routes_page.set_from(address_from)
        routes_page.set_to(address_to)
        assert routes_page.get_from() == address_from
        assert routes_page.get_to() == address_to

        # Paso 2: Seleccionar tarifa Comfort
        routes_page.select_comfort()
        assert "comfort" in self.driver.find_element(*routes_page.comfort_button).get_attribute('class')

        # Paso 3: Rellenar número de teléfono
        routes_page.enter_phone_number(data.phone_number)
        assert self.driver.find_element(*routes_page.phone_field).get_property('value') == data.phone_number

        # Paso 4: Agregar tarjeta de crédito
        routes_page.add_credit_card(data.card_number, data.card_code)
        assert "success" in self.driver.find_element(By.ID, 'card-status').text

        # Paso 5: Escribir un mensaje para el conductor
        routes_page.write_message_for_driver(data.message_for_driver)
        assert routes_page.driver.find_element(*routes_page.message_field).get_property('value') == data.message_for_driver

        # Paso 6: Pedir manta y pañuelos
        routes_page.request_blanket_and_tissues()
        assert "selected" in self.driver.find_element(*routes_page.blanket_button).get_attribute('class')
        assert "selected" in self.driver.find_element(*routes_page.tissues_button).get_attribute('class')

        # Paso 7: Pedir 2 helados
        routes_page.order_ice_cream(2)
        assert int(self.driver.find_element(By.ID, 'ice-cream-counter').text) == 2

        # Paso 8: Validar que el modal de taxi aparece
        routes_page.wait_for_taxi_modal()
        assert self.driver.find_element(*routes_page.taxi_modal).is_displayed()

        # Paso 9: Validar que aparece la información del conductor
        routes_page.wait_for_driver_info()
        assert self.driver.find_element(*routes_page.driver_info).is_displayed()

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()
