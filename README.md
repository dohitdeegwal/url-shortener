# URL Shortner
#### Description:

This is a very basic URL shortening web application.

A URL is considered valid if it "looks like" a URL. This gets determined through parsing with a regular expression. This is notoriously hard (impossible?) to get right, so this program is only approximately right in that regard. The alternative would be to try and actually connect to the URL, perhaps with a HEAD request. That approach has a couple of drawbacks, though. For one, it is more time consuming. And secondly, it would reject resources that are temporarily unavailable.


I have used python to write the controller code of the appplication.
I have used Flask as the framework for this web application
I have used HTML for all the webpages
I have used CSS to design all my pages

So, this application has two routes
'/' route and '/surl' route

The '/' route supports two methods viz GET and POST
When the page is requested via GET method the index page with form to shorten the URL is displayed
When the method used is POST the input (ourl i.e. original URL) is assigned a unique 7 character alphanumeric code which uniquely identifies the Original URL

When the user Visits the'/surl' route where surl is shortened url, application queries the SQL database for the ourl (original URL) associated with the surl (shortened URL)
and the redirect function the redirects the user to the destination page
