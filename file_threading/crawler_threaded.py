import os
import random
import shutil
import lazynlp
from pybloom import BloomFilter
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor

class MultiThreadScraper:

    def __init__(self, input_path, output_path):

        self.input_path = input_path
        self.output_path = output_path
        self.pool = ThreadPoolExecutor(max_workers=15)
        self.to_crawl = Queue()

    def download_pages(self,filename):
        print(" Calling download for " + filename)
        lazynlp.download_pages(
            self.input_path + "/" + filename, 
            self.output_path + "/" + filename, 
            timeout=5, default_skip=True, extensions=[], domains=[]
            )
        return

    def load_reddit_urls(self):
        files = os.listdir(self.input_path)
        for filename in files:
            self.to_crawl.put(filename)
        return

    def post_scrape_callback(self, res):
        print("  Job complete   ")

    def run_scraper(self):
        self.load_reddit_urls()
        while True:
            try:
                filename = self.to_crawl.get(timeout=60)
                print("Scraping file: {}".format(filename))
                job = self.pool.submit(self.download_pages, filename)
                job.add_done_callback(self.post_scrape_callback)
            except Empty:
                return
            except Exception as e:
                print(e)
                continue

if __name__ == '__main__':
    s = MultiThreadScraper("/gpfs/gpfsfpo/reddit_urls/1","/gpfs/gpfsfpo/reddit_dataset/1")
    s.run_scraper()    


