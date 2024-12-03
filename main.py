import data
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

class UrbanRoutesPage:
    # Selectores
    from_field = (By.ID, 'from')  # Campo "Desde"
    to_field = (By.ID, 'to')  # Campo "Hasta"
    comfort_tariff = (By.XPATH, "//img[@alt='Comfort']")  # Imagen "Comfort"
    phone_field = (By.XPATH, "(//input[@id='phone'])[2]")  # Segundo campo de teléfono
    add_card_button = (By.XPATH, "//div[contains(text(),'Agregar tarjeta')]")  # Botón de agregar tarjeta
    card_number_field = (By.ID, 'number')  # Campo de número de tarjeta
    card_cvv_field = (By.XPATH, "(//input[@id='code'])[2]")  # Segundo campo de código CVV
    link_card_button = (By.XPATH, "//button[contains(text(),'Agregar')]")  # Botón para agregar tarjeta
    message_field = (By.ID, 'comment')  # Campo para escribir mensaje
    blanket_button = (By.ID, 'blanket')  # Botón para solicitar una manta 
    napkins_button = (By.ID, 'napkins')  # Botón para solicitar servilletas 
    ice_cream_button = (By.XPATH, "//div[contains(text(),'Helado')]")  # Botón para solicitar helado
    driver_info = (By.ID, 'driver-info')  # Información del conductor

    def __init__(self, driver):
        self.driver = driver

    def set_from(self, from_address):
        self.wait_for_element(*self.from_field)
        self.driver.find_element(*self.from_field).send_keys(from_address)

    def set_to(self, to_address):
        self.wait_for_element(*self.to_field)
        self.driver.find_element(*self.to_field).send_keys(to_address)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def select_comfort_tariff(self):
        self.wait_for_element(*self.comfort_tariff)
        self.driver.find_element(*self.comfort_tariff).click()

    def fill_phone_number(self, phone_number):
        self.wait_for_element(*self.phone_field)
        phone_input = self.driver.find_element(*self.phone_field)
        phone_input.send_keys(phone_number)

    def add_credit_card(self, card_number, card_code):
        self.wait_for_element(*self.add_card_button)
        self.driver.find_element(*self.add_card_button).click()  # Hacemos clic en "Agregar tarjeta"
        self.driver.find_element(*self.card_number_field).send_keys(card_number)  # Ingresar el número de tarjeta
        cvv_field = self.driver.find_element(*self.card_cvv_field)  # Buscar el campo del CVV
        cvv_field.send_keys(card_code)  # Ingresar el código de la tarjeta (CVV)
        cvv_field.send_keys(Keys.TAB)  # Simulamos la tecla TAB para cambiar el foco a otro campo
        self.wait_for_element(*self.link_card_button)  # Esperamos que el botón "Vincular tarjeta" esté visible
        self.driver.find_element(*self.link_card_button).click()  # Hacemos clic en el botón de vinculación de tarjeta

    def write_message(self, message):
        self.wait_for_element(*self.message_field)
        message_input = self.driver.find_element(*self.message_field)
        message_input.send_keys(message)

    def request_blanket(self):
        self.wait_for_element(*self.blanket_button)
        self.driver.find_element(*self.blanket_button).click()

    def request_napkins(self):
        self.wait_for_element(*self.napkins_button)
        self.driver.find_element(*self.napkins_button).click()

    def request_ice_cream(self, quantity):
        for _ in range(quantity):
            self.wait_for_element(*self.ice_cream_button)
            self.driver.find_element(*self.ice_cream_button).click()

    def wait_for_element(self, by, value, timeout=30): 
        return WebDriverWait(self.driver, timeout).until(
            expected_conditions.visibility_of_element_located((by, value))
        )

    def wait_for_driver_info(self, timeout=10):
        self.wait_for_element(By.ID, 'driver-info', timeout)

    def is_driver_info_visible(self):
        return self.driver.find_element(*self.driver_info).is_displayed()


class TestUrbanRoutes:

    driver = None

    @classmethod
    def setup_class(cls):
        cls.driver = webdriver.Chrome()

    def test_set_route(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        address_from = data.address_from
        address_to = data.address_to
        routes_page.set_from(address_from)
        routes_page.set_to(address_to)
        assert routes_page.get_from() == address_from
        assert routes_page.get_to() == address_to

    def test_select_comfort_tariff(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.select_comfort_tariff()

    def test_fill_phone_number(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.fill_phone_number(data.phone_number)

    def test_add_credit_card(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.add_credit_card(data.card_number, data.card_code)

    def test_write_message(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.write_message(data.message_for_driver)

    def test_request_blanket_and_napkins(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.request_blanket()
        routes_page.request_napkins()

    def test_request_ice_cream(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.request_ice_cream(2)

    def test_wait_for_driver_info(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        routes_page.wait_for_driver_info()
        assert routes_page.is_driver_info_visible()

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()
