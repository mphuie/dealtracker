import urllib2
import re
import sqlite3
import datetime
conn = sqlite3.connect('dashboard.sqlite')
c = conn.cursor()



def pulldeals(url):
	response = urllib2.urlopen(url)
	html = response.read()

	now = datetime.datetime.now()

	for match in re.finditer(r'(?sm)<tr id="t\d+"[^<]+>.*?^</tr>', html):
		post_html = match.group()

		match_post = re.search(r'<a href="/forums/hot-deals/(\d+)/" class="topicTitle"[^<]+>(.*?)</a>', post_html, re.DOTALL | re.MULTILINE)
		if match_post:
			post_id = match_post.group(1)
			post_title = match_post.group(2)
			post_title = re.sub("'", "''", post_title)
			match_post = re.search(r"rating: (-?\d+)", post_html)
			if match_post:
				rating = match_post.group(1)
			else: 
				rating = -1
			match_post = re.search(r'<td class="topicInfo">\s*(\d+)\s*</td>', post_html, re.IGNORECASE)
			if match_post:
				replycount = match_post.group(1)
			else:
				replycount = -1
		
			match_post = re.search(r"(\d+ days?|New)\s+<br />\s+(\d+) Views", post_html)
			if match_post:
				post_date = match_post.group(1)
				post_date = re.sub(r"\sdays?", "", post_date)
				if post_date != 'New':
					diff = datetime.timedelta(days=int(post_date))
					post_date = now - diff
				else:
					post_date = now
				viewcount = match_post.group(2)
			else:
				viewcount = -1
			
			match_post = re.search(r"<a[^<]+last post[^<]+>[^<]+<br/>\s+([\d/:ap ]+)</a>", post_html)
			if match_post:
				last_post_date = match_post.group(1).strip() + 'm'
				last_post_date_object = datetime.datetime.strptime(last_post_date, "%m/%d/%y %I:%M%p")
				diff = datetime.timedelta(hours=2)
				last_post_date_object = last_post_date_object - diff
				last_post_timestamp = last_post_date_object.strftime('%Y-%m-%d %H:%M:%S')
				# print last_post_timestamp
			# print "[%s] [%s] %s" % (post_id, post_date, post_title)
			source = 'fatwallet'

			c.execute("SELECT id FROM deals_deal WHERE post_id = '%s'" % post_id)
			row = c.fetchone()
			if row is None:
				print "Deal not in DB!"
				c.execute("INSERT INTO deals_deal (title, post_date, source, post_id, last_post_date) VALUES ('%s', '%s', '%s', %s, '%s')" % (post_title, post_date, source, post_id, last_post_timestamp))
				db_id = c.lastrowid
				c.execute("INSERT INTO deals_dealstatus (deal_id, replycount, viewcount, rating, t) VALUES (%s, %s, %s, %s, '%s')" % (db_id, replycount, viewcount, rating, now))
			else:
				c.execute("UPDATE deals_deal SET last_post_date = '%s' WHERE id = %s" % (last_post_timestamp, row[0]))
				c.execute("INSERT INTO deals_dealstatus (deal_id, replycount, viewcount, rating, t) VALUES (%s, %s, %s, %s, '%s')" % (row[0], replycount, viewcount, rating, now))
			
pulldeals('http://www.fatwallet.com/forums/hot-deals/')
pulldeals('http://www.fatwallet.com/forums/hot-deals/?start=18')
pulldeals('http://www.fatwallet.com/forums/hot-deals/?start=38')
conn.commit()
c.close()
