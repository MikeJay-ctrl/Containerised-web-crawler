import 	sys
import 	xmlrunner
import 	unittest
import 	mock
from 	unittest.mock 	import patch
from 	crawler			import Crawler

class TestCrawler(unittest.TestCase):


	@mock.patch('crawler.Crawler.attempt_connection')
	def test_check_for_sitemap_fail(self, mock_attempt_conn):

		test_set = [400, 401, 404, 500, 501, 503]
		crawler = Crawler("http://exampleimaginarysite.org")

		for idx in range(len(test_set)):
			crawler.attempt_connection.return_value = mock.MagicMock(content= b'error', \
																	status_code= test_set[idx])
			crawler.check_for_sitemap()

			assert crawler.unvisited == set([])



	@mock.patch('crawler.Crawler.attempt_connection')
	def test_check_for_sitemap_success(self, mock_attempt_conn):

		test_set 	= [200, 201]
		dummy_xml 	= self.get_dummy_data('dummy.xml')
		crawler 	= Crawler("http://exampleimaginarysite.org")
		
		for idx in range(len(test_set)):
			crawler.attempt_connection.return_value = mock.MagicMock(content= dummy_xml, \
																	status_code= test_set[idx])
			crawler.check_for_sitemap()

			assert crawler.unvisited == set(["http://exampleimaginarysite.org/imaginaryloc1", "http://exampleimaginarysite.org/imaginaryloc2"])



	def test_extract_xml_data(self):
		expected_result1 =  ["http://exampleimaginarysite.org/imaginaryloc1", "http://exampleimaginarysite.org/imaginaryloc2"]
		expected_result2 =  ["0ea692529d6b3642cff358eb77781998", "89596f265172f57ceb90e8d864fd21a0"]
		
		dummy_xml 	= self.get_dummy_data('dummy.xml').decode("UTF-8")
		crawler 	= Crawler("http://exampleimaginarysite.org")

		result1 = crawler.extract_xml_data(dummy_xml, 'loc')
		result2 = crawler.extract_xml_data(dummy_xml, 'content:hash')

		assert result1 == expected_result1
		assert result2 == expected_result2



	def test_extract_asset_data(self):
		baseurl 		= 'http://exampleimaginarysite.org'
		test_file_name	= 'dummy.html'
		unwanted_links	= ['prefetch', 'dns-prefetch', 'preconnect', 'preload', 'pingback']
		unwanted_exts 	= ['#', '/#', '/cdn-cgi/']

		expected_result = {test_file_name: {'assets': ["http://exampleimaginarysite.org/icons/dummy_img.png", "http://exampleimaginarysite.org/scripts/dummyScript.js", "http://exampleimaginarysite.org/css/dummy_css1.css", "http://exampleimaginarysite.org/css/dummy_css2.css"]}}
		file_handle 	= open(test_file_name, 'rb')

		crawler 		= Crawler(baseurl)
		crawler.init_preferences(unwanted_links, unwanted_exts)

		crawler.extract_asset_data(file_handle, test_file_name)
		result = crawler.visited
		file_handle.close()
		print(result)
		assert result == expected_result



	def get_dummy_data(self, filename):
		file_handle = open(filename, 'rb')
		dummy_data 	= file_handle.read()
		file_handle.close()
		return dummy_data




if __name__ == '__main__':
	unittest.main(
		testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
		failfast=False, buffer=False, catchbreak=False)

