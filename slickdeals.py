import urllib2
import re
import sqlite3
import datetime


conn = sqlite3.connect('dashboard.sqlite')
c = conn.cursor()

response = urllib2.urlopen('http://slickdeals.net/forums/forumdisplay.php?f=9')
html = response.read()

today = datetime.date.today()
now = datetime.datetime.now()


for match in re.finditer('(?s)<tr id="sdpostrow_\d+">.*?</tr>', html):
	post_html = match.group()

	match_post = re.search(r"<a href=[^<]+thread_title_(\d+)[^<]+>(.*?)</a>", post_html, re.DOTALL)
	if match_post:
		post_id = match_post.group(1)
		post_title = match_post.group(2)
		post_title = re.sub("'", "''", post_title)
	
	match_post = re.search(r"Replies: ([\d,]+),\s+Views: ([\d,]+)", post_html, re.DOTALL)
	if match_post:
		replycount = match_post.group(1)
		viewcount = match_post.group(2)
		viewcount = re.sub(",", "", viewcount)
		replycount = re.sub(",", "", replycount)
		
	match_post = re.search(r"Score: (-?\d+)", post_html, re.IGNORECASE)
	if match_post:
		rating = match_post.group(1)
	else:
		rating = 0
		
	match_post = re.search(r'(Today|\d{2}-\d{2}-\d{4})\s+<span class="time">(.*?)</span>', post_html, re.IGNORECASE)
	if match_post:

		day = match_post.group(1)
		time = match_post.group(2)
		
		if day == "Today":
			day = str(today)
			
		posttimestamp = "%s %s" % (day, time)
	
		if re.search(r"\d{2}-\d{2}-\d{4}", day):
			post_date = datetime.datetime.strptime(posttimestamp, "%m-%d-%Y %I:%M %p")
			posttimestamp = post_date.strftime('%Y-%m-%d %H:%M:%S')
		else:
			post_date = datetime.datetime.strptime(posttimestamp, "%Y-%m-%d %I:%M %p")
			posttimestamp = post_date.strftime('%Y-%m-%d %H:%M:%S')

		print posttimestamp

	match_post = re.search(r'  <!-- Last Post -->(.*?)</span><br />\s+<a href="/forums/member\.php\?find=lastposter[^<]+>', post_html, re.DOTALL)
	if match_post:
		last_post_date = match_post.group(1)
		last_post_date = re.sub("(?s)<[^<]+>", "", last_post_date)
		last_post_date = last_post_date.strip()
		if 'Today' in last_post_date:
			last_post_date = re.sub("Today", "", last_post_date)
			last_post_date = str(today) + last_post_date
			last_post_date = datetime.datetime.strptime(last_post_date, "%Y-%m-%d %I:%M %p").strftime('%Y-%m-%d %H:%M:%S')
		else:
			last_post_date = datetime.datetime.strptime(last_post_date, "%m-%d-%Y %I:%M %p").strftime('%Y-%m-%d %H:%M:%S')
		print "Last post date: %s" % (last_post_date)

	source = 'slickdeals'
	c.execute("SELECT id FROM deals_deal WHERE post_id = '%s'" % post_id)
	row = c.fetchone()
	if row is None:
	# print "[%s] %s (%s rating, %s views, %s replies) %s" % (post_id, posttimestamp, rating, viewcount, replycount, post_title)
		query = "INSERT INTO deals_deal (title, post_date, source, post_id, last_post_date) VALUES ('%s', '%s', '%s', %s, '%s')" % (post_title, posttimestamp, source, post_id, last_post_date)	
		c.execute(query)
		db_id = c.lastrowid
		query = "INSERT INTO deals_dealstatus (deal_id, replycount, viewcount, rating, t) VALUES (%s, %s, %s, %s, '%s')" % (db_id, replycount, viewcount, rating, now)
		print query
		c.execute(query)
	else:
		

		query = "UPDATE deals_deal SET last_post_date = '%s' WHERE id=%s" % (last_post_date, row[0])
		print query
		c.execute(query)
		query = "INSERT INTO deals_dealstatus (deal_id, replycount, viewcount, rating, t) VALUES (%s, %s, %s, %s, '%s')" % (row[0], replycount, viewcount, rating, now)
		print query
		c.execute(query)
conn.commit()
c.close()
