import time
import random
import logging
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
CONFIG = {
    "appium_server_url": "http://localhost:4723",
    "capabilities": {
        "platformName": "Android",
        "automationName": "UiAutomator2",
        "appPackage": "com.zhiliaoapp.musically", # TikTok phổ biến nhất
        "appActivity": "com.ss.android.ugc.aweme.splash.SplashActivity",
        "noReset": True,
        "newCommandTimeout": 300,
        "ensureWebviewsHavePages": True,
    },
    "tag_user": "@abcxyx",
    "max_comments": 15,  # Giới hạn số comment mỗi lần chạy
    "delay": {
        "min": 10,
        "max": 35,
        "swipe_duration": 1200, # ms
        "watch_min": 10, # Giây xem video tối thiểu
        "watch_max": 25, # Giây xem video tối đa
    },
    "vietnamese_templates": [
        "Chào bạn {tag}, video hay quá!",
        "Tuyệt vời quá {tag} ơi!",
        "Đúng là {tag} có khác, chất lượng thật!",
        "Cảm ơn {tag} đã chia sẻ nhé.",
        "Mọi người vào xem {tag} này!",
        "Video này cuốn quá {tag} nhỉ?",
        "Cái này lạ nè {tag}, bạn thấy sao?",
        "Đỉnh cao luôn {tag}!",
        "Không thể tin được {tag} làm được luôn.",
        "Thả tim cho {tag} nhé <3",
        "Video hữu ích quá {tag}!",
        "Sáng tạo quá {tag}, tiếp tục phát huy nhé.",
        "Mình rất thích nội dung của {tag}.",
        "Bạn {tag} làm video công phu quá.",
        "Ủng hộ {tag} hết mình luôn!",
        "Ghé thăm {tag} thôi cả nhà ơi.",
    ]
}

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class TikTokBot:
    def __init__(self, config):
        self.config = config
        self.options = UiAutomator2Options().load_capabilities(config["capabilities"])
        self.driver = None
        self.comment_count = 0

    def start(self):
        logger.info("Starting Appium session...")
        try:
            self.driver = webdriver.Remote(self.config["appium_server_url"], options=self.options)
            logger.info("Connected to device.")
        except Exception as e:
            logger.error(f"Failed to connect to Appium: {e}")
            raise

    def stop(self):
        if self.driver:
            self.driver.quit()
            logger.info("Session closed.")

    def recover(self):
        """Hàm phục hồi khi bị kẹt: back và swipe để về feed chính."""
        logger.info("Attempting recovery...")
        try:
            for _ in range(3):
                self.driver.back()
                time.sleep(1)
            self.human_swipe()
        except:
            pass

    def random_delay(self):
        wait_time = random.uniform(self.config["delay"]["min"], self.config["delay"]["max"])
        logger.info(f"Random delay: {wait_time:.2f}s...")
        time.sleep(wait_time)

    def human_swipe(self):
        """Vuốt chậm, ổn định hơn với ActionBuilder."""
        try:
            size = self.driver.get_window_size()
            start_x = size['width'] // 2 + random.randint(-30, 30)
            start_y = int(size['height'] * 0.8) + random.randint(-20, 20)
            end_y = int(size['height'] * 0.2) + random.randint(-20, 20)

            actions = ActionChains(self.driver)
            actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.move_to_location(start_x, end_y, duration=self.config["delay"]["swipe_duration"])
            actions.w3c_actions.pointer_action.release()
            actions.perform()
            logger.info("Swiped to next video.")
        except Exception as e:
            logger.error(f"Swipe failed: {e}")

    def random_touch(self):
        """Chạm ngẫu nhiên ổn định."""
        try:
            size = self.driver.get_window_size()
            x = random.randint(200, size['width'] - 200)
            y = random.randint(300, size['height'] - 300)
            
            actions = ActionChains(self.driver)
            actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(x, y)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.1)
            actions.w3c_actions.pointer_action.pointer_up()
            actions.perform()
            logger.info(f"Random touch at ({x}, {y})")
        except Exception as e:
            logger.error(f"Touch failed: {e}")

    def find_element_safe(self, selectors, timeout=5):
        """Thử nhiều selector để tìm element an toàn."""
        for by, value in selectors:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
                return element
            except:
                continue
        return None

    def open_comments(self):
        """Mở phần bình luận bằng nhiều cách tìm button."""
        selectors = [
            (AppiumBy.ACCESSIBILITY_ID, "Comments"),
            (AppiumBy.XPATH, "//*[contains(@content-desc, 'comment') or contains(@content-desc, 'bình luận')]"),
            (AppiumBy.ID, "com.zhiliaoapp.musically:id/b_k"), # Resource ID ví dụ
        ]
        btn = self.find_element_safe(selectors)
        if btn:
            btn.click()
            logger.info("Opened comment section.")
            return True
        logger.warning("Could not find comment button.")
        return False

    def post_comment(self):
        """Gửi bình luận với nhiều cách tìm input và button Post."""
        try:
            # 1. Tìm và click Input
            input_selectors = [
                (AppiumBy.XPATH, "//*[contains(@text, 'Add comment') or contains(@text, 'Thêm bình luận')]"),
                (AppiumBy.CLASS_NAME, "android.widget.EditText"),
            ]
            input_field = self.find_element_safe(input_selectors)
            if not input_field:
                return False
            
            input_field.click()
            time.sleep(1.5)

            # 2. Nhập text (Ưu tiên active_element)
            template = random.choice(self.config["vietnamese_templates"])
            comment_text = template.format(tag=self.config["tag_user"])
            
            active_input = self.driver.switch_to.active_element
            active_input.send_keys(comment_text) # Hoặc dùng set_value nếu được hỗ trợ
            logger.info(f"Inputted: {comment_text}")
            time.sleep(1)

            # 3. Tìm và click nút Send/Post
            send_selectors = [
                (AppiumBy.ACCESSIBILITY_ID, "Post comment"),
                (AppiumBy.ACCESSIBILITY_ID, "send"),
                (AppiumBy.XPATH, "//*[contains(@text, 'Post') or contains(@text, 'Gửi') or contains(@content-desc, 'Post')]"),
            ]
            send_btn = self.find_element_safe(send_selectors)
            if send_btn:
                send_btn.click()
                logger.info("Comment posted.")
                self.comment_count += 1
                time.sleep(1)
                self.driver.back() # Đóng phím ảo hoặc khung comment
                return True
        except Exception as e:
            logger.error(f"Error in post_comment: {e}")
        
        self.driver.back()
        return False

    def run_cycle(self):
        """Một chu kỳ: xem, chạm, comment, swipe."""
        # 1. Xem video lâu hơn (Human behavior)
        watch_time = random.randint(self.config["delay"]["watch_min"], self.config["delay"]["watch_max"])
        logger.info(f"Watching video for {watch_time}s...")
        time.sleep(watch_time)

        # 2. Tương tác ngẫu nhiên
        if random.random() > 0.6:
            self.random_touch()

        # 3. Comment
        if self.open_comments():
            time.sleep(2)
            if self.post_comment():
                self.random_delay()
            else:
                logger.info("Failed to post comment, moving on.")

        # 4. Chuyển video
        self.human_swipe()

if __name__ == "__main__":
    bot = TikTokBot(CONFIG)
    try:
        bot.start()
        max_c = CONFIG["max_comments"]
        
        while bot.comment_count < max_c:
            logger.info(f"--- Comment Progress: {bot.comment_count}/{max_c} ---")
            bot.run_cycle()
            
            # Thỉnh thoảng recover để đảm bảo không bị kẹt
            if bot.comment_count % 5 == 0 and bot.comment_count > 0:
                bot.recover()
                
        logger.info(f"Reached max comments ({max_c}). Task finished.")
    except KeyboardInterrupt:
        logger.info("Stopped by user.")
    except Exception as e:
        logger.critical(f"Main loop error: {e}")
        bot.recover()
    finally:
        bot.stop()
