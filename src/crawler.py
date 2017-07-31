import 	sys
import 	json
import 	requests
import 	re
import	urllib.parse 	
import 	traceback

from 	bs4 			import BeautifulSoup
from 	argparse 		import ArgumentParser




class Crawler:
	def __init__(self, baseurl):
		self.initialise_variables(baseurl)


	def initialise_variables(self, baseurl):
		'''
			Description:
							Initialises instance variables
			Args:
							baseurl : str - containing url to begin crawl
			returns:
							none
		'''
		self.baseurl 			= baseurl
		self.unvisited 			= set([])
		self.visited 			= {}
		self.asset_data 		= []
		self.errorLog 			= []
		self.progress 			= 0
		self.max_progress 		= 15
		self.init_preferences()




	def init_preferences(self, unwanted_links=[], unwanted_extensions=[]):
		'''
			Description:
							Allows the user to supply any links 'rel' arguments or url extensions they wish to 
							omit from search based on prior knowledge of site
			Args:
							unwanted_links 			: 	list(str) 	list of strings of <link 'rel' > args the user wishes to omit from results
														Default value = [], and all data will be permitted

							unwanted_extensions 	: 	list(str) 	list of strings of unwanted url extensions args the user wishes to omit from results
														Default value = [], and all valid urls 
			Returns:
							none
		'''
		self.unwanted_links = unwanted_links
		self.unwanted_extensions = unwanted_extensions




	def check_for_sitemap(self):
		'''
			Description:
							Checks for presence of sitemap in standard location (Basedir/sitemap.xml)
			Args:
							none
			Returns:
							none
		'''
		response = self.attempt_connection(self.baseurl+'/sitemap.xml')
		if response.status_code // 100 == 2:
			content = response.content.decode("utf-8")
			self.unvisited = set([urllib.parse.urljoin(self.baseurl, x) for x in self.extract_xml_data(content, "loc")])
		elif response.status_code // 100 == 4:
			print('Sitemap.xml not found')
		elif response.status_code // 100 == 5:
			print('unknown server error when retrieving sitemap.xml')




	def begin_crawl(self):
		'''
			Description:
							checks for presence of sitemap then begins crawl based on values present in self.unvisited
			Args:
							none
			Returns:
							none
		'''
		self.check_for_sitemap()
		
		if len(self.unvisited) == 0:
			self.unvisited.add(self.baseurl)
		
		while len(self.unvisited) > 0:
			try:
				page_url = self.unvisited.pop()
				response = self.attempt_connection(page_url)
				if response.status_code //100 == 2:
					self.extract_asset_data(response.content.decode("UTF-8"), page_url)
				else:
					pass
			except Exception as e:
				self.errorLog.append("Exception when visiting" + str(page_url) +'\n')
				traceback.print_exc()
			

		preferred_format = [{'url': key, 'assets': self.visited[key]['assets']} for key in list(self.visited.keys())]
		self.pretty_asset_data = json.dumps(preferred_format, sort_keys=False, indent=4, separators=(',', ':'))




	def view_visited(self):
		''' 
			Description:
							Allows the user to view the asset data from visited sites in a JSON formatted list
			Args:
							none
			Returns:		
							none
		'''
		if self.pretty_asset_data:
			print(self.pretty_asset_data)




	def extract_asset_data(self, page_data, page_url):
		'''
			Description:
							Checks for the presence of static assets when given a page url and a binary representation of HTML data
			Args:
							page_data 	:    b'' 	binary representation of xml data
							page_url 	: 	 str 	The url of the page the data belongs to
			Returns:
							none
		'''
		self.update_user()	

		soup = BeautifulSoup(page_data, "html.parser")

		if page_url not in self.visited:
			self.visited[page_url] = {'assets' : []}

			for item in ['img', 'script', 'source', 'a', 'link']:
				assets = soup.findAll(item)

				for asset in assets:
					if asset.has_attr('src'):
						self.append_asset_to_page(asset['src'], page_url)

					if asset.has_attr('href'):
						if item == 'link': 
							if asset['rel'][0] in self.unwanted_links:
								continue
							elif asset['rel'][0] in ['stylesheet', 'icon', 'apple-touch-icon', 'apple-touch-icon-precomposed']:
								self.append_asset_to_page(asset['href'], page_url)
			
						normalised_ref = urllib.parse.urljoin(self.baseurl, asset['href'])
						if asset['href'] not in self.visited and self.valid_pattern(asset['href']):
							if normalised_ref[-4:] not in ['.png', '.pdf']:
								self.unvisited.add(normalised_ref)
							else:
								self.append_asset_to_page(normalised_ref, page_url)


								


	def append_asset_to_page(self, asset, page):
		'''
			Description:
							Helper method, appends an asset to the list assigned to a list of assets 
							associated with the page_url in the visited dictionary
			Args:
							asset 	: 	str 	url containing location of static element
							page 	: 	str 	url of page that where the asset tag was found
			Returns:
							none
		'''
		self.visited[page]['assets'].append(urllib.parse.urljoin(self.baseurl, asset))




	def attempt_connection(self, location):
		'''
			Description:
							Helper method, attempts a HTTP GET request to a given location
			Args:
							location 	: 	str 	url of page to be requested
			Returns:
							none
		'''
		try:
			r = requests.get(location)
			return r
		except Exception as e:
			print("Unknown Error when attempting to connect to {}".format(location) + str(e))




	def valid_pattern(self, page):
		'''
			Description:
							Checks if a given url is a valid pattern. That is is it derivitive of our base directory
			Args:
							page 		: 	str 	url containing location potential new page
			Returns:
							Boolean		: 	True if valid pattern, else False
		'''
		normalised_page 	= urllib.parse.urljoin(self.baseurl, page)

		pattern = r'^({})[-a-zA-Z0-9@:%_\+.~#?&//=]*?'.format(self.baseurl)
		result 	= pattern.match(normalised_page)
		
		if not result or self.is_known_redirect(normalised_page):
			return False
		return True




	def is_known_redirect(self, normalised_page):
		'''
			Description:
							Checks if given url matches any known patterns of circular redirect pages, 
			Args:
							normalised_page 	: 	str 	url containing location of static element
			Returns:
							Boolean				: 	True if known redirect, else False
		'''
		for extension in self.unwanted_extensions:

			pattern = r'^({}){}[-a-zA-Z0-9@:%_\+.~#?&//=]*?'.format(self.baseurl, extension)
			pattern = re.compile(pattern)
			result 	= pattern.match(normalised_page)

			if result:
				return True
		return False




	def extract_xml_data(self, content, tag_type):
		'''
			Description:
							Extract xml data from a caller specified tag type
			Args:
							content 	: 	str 	binary representation of xml data
							tagType 	: 	str 	name of tag 
			Returns:
							list(str()) : 	list of strings containing information from given tags
		'''
		ltrim = len(tag_type) + 2
		rtrim = len(tag_type) + 3
		return [match[ltrim: -rtrim] for match in re.findall(r"<{}>\s?[.\/:0-9a-zA-Z-]+\s?<\/{}>".format(tag_type, tag_type), content)]



	def update_user(self):
		'''
			Description:
							Text based indicator to show the user crawler is still running, and inform how many
							unvisited links remain
			Args:
							none
			Returns:
							none
		'''
		new_position = self.progress % self.max_progress+1
		sys.stdout.write('Working [{}{}]  {} Pages remaining in search queue\r'.format('#'*new_position, ' '*(self.max_progress-new_position), len(self.unvisited)))
		sys.stdout.flush()
		self.progress = self.progress+1




def is_url_valid(url):
	'''
		Description:
						Validate a user supplied URL
		Args:
						url 		: 	str 	containing url supplied via command line args
		Returns:
						Boolean		: 	True if valid, else False
	'''
	pattern = r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$"
	pattern = re.compile(pattern)
	result = pattern.match(url)
	if result:
		return True
	return False





if __name__ == '__main__':

	parser = ArgumentParser(description="Gather Options")
	parser.add_argument("-u", "--url", dest="a_baseurl", help="Base url of the site to be crawled", default="https://bbc.com")
	parser.add_argument("-ul", "--unwanted_links", dest="a_unwantedLinks", help="space separated list of which link 'rel' attributes to ignore", nargs="+", type=str, default=['prefetch', 'dns-prefetch', 'preconnect', 'preload', 'pingback'] )
	parser.add_argument("-ue", "--unwanted_extensions", dest="a_unwantedExtensions", help="space separated list of which extensions to ignore", nargs="+", type=str, default=['#', '/#', '/cdn-cgi/'])

	args = vars(parser.parse_args())

	if is_url_valid(args['a_baseurl']):
		c = Crawler(args['a_baseurl'])
		c.init_preferences(args['a_unwantedLinks'], args['a_unwantedExtensions'])
		c.begin_crawl()
		c.view_visited()
	else:
		print(args['help'])





