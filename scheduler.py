from job import scan_product_for_upscale
import schedule
import time

# create a scheduler
schedule.every(1).minutes.do(scan_product_for_upscale)

while True:
    schedule.run_pending()
    time.sleep(1)