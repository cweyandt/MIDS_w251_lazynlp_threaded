import os
import random
import shutil
import ssl
import lazynlp
import hashlib
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor

from analytics import *
from cleaner import *
from create import *
from crawl import *
from utils import *

class MultiThreadScraper:

    def __init__(self, link_file, output_path, ):

        self.link_file = link_file
        self.output_path = output_path
        self.pool = ThreadPoolExecutor(max_workers=20)
        self.to_crawl = Queue()

        self.index_file = os.path.join(output_path, 'index.urls')
        self.idx = 0
        self.links = open(link_file, 'r')
        self.extensions = []
        self.domains = []
        self.timeout = 5

        if os.path.isdir(output_path) and os.path.exists(self.index_file):
            """ If index file exists, we've downloaded from this list of
            URLs before, continue from where it left off the last time.
            """
            self.idx, self.links = get_current_idx(self.index_file, self.links)
            print("Resuming from index: " + str(self.idx))
        else:
            os.makedirs(output_path, exist_ok=True)

        self.index = open(os.path.join(output_path, 'index.urls'), 'a')
        self.skipped_urls = open(os.path.join(output_path, 'skip.urls'), 'a')
        self.bad_connection_urls = open(os.path.join(output_path, 'connection.urls'), 'a')
        self.bad_urls = open(os.path.join(output_path, 'bad.urls'), 'a')
        self.non_ascii_urls = open(os.path.join(output_path, 'non_ascii.urls'), 'a')
        self.empty_urls = open(os.path.join(output_path, 'empty.urls'), 'a')

        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

        self.hashed = hashlib.sha1()

        ext_lines = open(f'./exclude_extensions.txt', 'r').readlines()
        self.extensions.extend([line.strip() for line in ext_lines])
        domain_lines = open(f'./exclude_domains.txt', 'r').readlines()
        self.domains.extend([line.strip() for line in domain_lines])


    def download_pages(self,filename):
        print(" Calling download for " + filename)
        process_links(
            self.input_path + "/" + filename, 
            self.output_path, 
            timeout=30, default_skip=True, extensions=[], domains=[]
            )
        return

    def load_reddit_urls(self):
        files = os.listdir(self.input_path)
        for filename in files:
            self.to_crawl.put(filename)
        return

    def post_scrape_callback(self, res):
        print("  Job complete with result " + str(res))


    def process_links(self):

        for link in self.links:
            link = link.strip()
            
            if to_skip(link, self.extensions, self.domains):
                self.skipped_urls.write(link + '\n')
                print('Skipped ', link)
            else:
                job = self.pool.submit(self.pool_link, link, self.idx)
                job.add_done_callback(self.post_scrape_callback)

            self.idx += 1


    def pool_link(self, link, idx):
        print(" Pooling link: " + str(idx) + "\t" + str(link))
        try:
            code, page = download_page(link, self.ctx, self.timeout)
        except:
            print( "failure with code " + str(code) )
            return
        
        if code == 1:
            self.bad_urls.write(link + '\n')
        elif code == 2:
            self.non_ascii_urls.write(link + '\n')
        elif code == 3:
            self.bad_connection_urls.write(link + '\n')
        
        if code > 0:
            return

        txt = clean_page(page)

        if not txt:
            print('Empty page', link)
            self.empty_urls.write(link + '\n')
            return

        print(idx, link)
        self.hashed.update(str(time.time()).encode())
        name = self.hashed.hexdigest()
        with open(f'{self.output_path}/{idx}_{name}.txt', 'w') as out:
            out.write(link + '\n' + txt)

        print(find_unprintable(txt))
        self.index.write('{}\n'.format(link))
        return


if __name__ == '__main__':
    s = MultiThreadScraper("./reddit_urls/reddit1.txt","./reddit_dataset/1")
    s.process_links()    

