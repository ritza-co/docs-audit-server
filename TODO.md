# TODO

## 28 May

* 
* Worker should be able to handle broken images ('couldn't fetch image') - if requests.get throws an error
* Worker should also report image HTTP codes - 404, 301, 200, etc and we should have another column in images that shows this
* We should combine tabs to have 

- Links tab
- - shows broken links at the top (coudln't fetch), followed by non-successful status codes, followed by OK status codes

- Images tab
- - shows broken images at the top (couldn't fetch) followed by non-successful status codes, followed by large images (above 100 KB, highlighted somehow), followed by all other images.

- Lighthouse tab
- Tatenda: remove this and put the data above as part of the overall summary.


* Rethink the routes so that the homepage redirects to dashboard and data is posted back to the /dashboard route too.

## 25 May
* LightHouse column - show performance, SEO, accessibility, and best practices per page and the worst performance number per collection
* Combine num links and link issues so "Broken links" -> 11/700
* Combine num images and image issues "Oversized images" -> 10/20.
* "Num URLs" -> integer showing just the number of URLs in the collection
* Remove task ID column from pending tasks


## 21 May

* Handle exceptions when requests.get throws an exception instead of getting an HTTP error code.



Results page for a single link

Link audit date <> 
Image audit date <>

[four tables, first two highighting issues, and next two showing all images and links.]

LINK ISSUES 
-----------
| URL | CODE 

IMAGE ISSUES
------------
| URL | SIZE

ALL IMAGES
-----------
| URL | SIZE

ALL LINKS
------------
| URL | CODE 

* Modify the worker to also pass info about working links and images (every status code and every image size) back to the server

* Remove the links from the tasks queue table IDs





---

* Move the front-ends from docs-audit to docs-server
* Move the input logic from docs-audit to docs-server (user can submit URLs)
* Write logic to create a 2 tasks for each URL the user submits (a link audit taks and an image audit task)
* Separate the tasks in the worker so only does the specific task
* Write logic in the server to understadn the output from the worker so it can idsplay these results to the user
* Create a loop in the worker to pull a new taks the moment it has submitted the results of the previous one - Sleep for 60 seconds if there are no tasks avialable and ask for another one then.


