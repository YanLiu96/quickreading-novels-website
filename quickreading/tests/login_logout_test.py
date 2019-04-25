from selenium import webdriver
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest


class UserLogin(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.verificationErrors = []
        self.accept_next_alert = True

    def test_user_login_logout(self):
        driver = self.driver
        driver.get("http://0.0.0.0:8001/")
        # General user
        driver.find_element_by_link_text("Login").click()
        driver.find_element_by_id("user_name").click()
        driver.find_element_by_id("user_name").clear()
        driver.find_element_by_id("user_name").send_keys("YanLiuTest")
        driver.find_element_by_id("user_password").click()
        driver.find_element_by_id("user_password").clear()
        driver.find_element_by_id("user_password").send_keys("123456")
        driver.find_element_by_id("user_login").click()
        driver.find_element_by_link_text("YanLiuTest").click()
        sleep(1)
        driver.find_element_by_xpath(
            "(.//*[normalize-space(text()) and normalize-space(.)='Payment'])[1]/following::span[2]").click()
        sleep(1)

        # VIP user
        driver.find_element_by_link_text("Login").click()
        driver.find_element_by_id("user_name").click()
        driver.find_element_by_id("user_name").clear()
        driver.find_element_by_id("user_name").send_keys("test1")
        driver.find_element_by_id("user_password").click()
        driver.find_element_by_id("user_password").clear()
        driver.find_element_by_id("user_password").send_keys("123456")
        driver.find_element_by_id("user_login").click()
        driver.find_element_by_link_text("test1").click()
        sleep(1)
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Renew VIP'])[1]/following::span[2]").click()
        sleep(1)

        # admin login logout
        driver.find_element_by_link_text("Login").click()
        driver.find_element_by_id("user_name").click()
        driver.find_element_by_id("user_name").clear()
        driver.find_element_by_id("user_name").send_keys("AdminYanLiu")
        driver.find_element_by_id("user_password").click()
        driver.find_element_by_id("user_password").clear()
        driver.find_element_by_id("user_password").send_keys("LY19961222..")
        driver.find_element_by_id("user_login").click()
        driver.find_element_by_link_text("AdminYanLiu").click()
        sleep(1)
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Payment'])[1]/following::span[2]").click()
        driver.close()

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
