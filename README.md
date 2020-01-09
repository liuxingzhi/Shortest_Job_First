# __Shortest Job First__
*CS411 Project, Team 309*
### Team members
- Xingzhi Liu
- Junfeng Lin
- Danjin Jiang
- Chenyu Fan
## Project Summary

#### <span><span>What we've accomplished</span></span>

<span><span>For the project, our team members built a fully functioning job finding website with advanced and creative features. We utilized development tools such as Python, Django, HTML, and Javascript in our project. Our site maintains a MySQL cloud database (via Amazon AWS) for data used in various systems in the project, including user system, job data crawling/posting/viewing system, and recommendation system. Our site has basic features such as user registration/login/logout/profile update, post/search/delete jobs, as well as advanced functions such as recommending jobs via email and a robust data crawler.</span></span>

#### Usefulness of our project

<span>There are many similar websites which can help users to do job search like</span> [<span>indeed.com/handshake</span>](http://indeed.com/handshake)<span>. But there are usually too many advertisements and it is not uncommon to find many jobs that are inappropriate and incomplete. The difference between our website and all the other similar websites is that we only crawl and post jobs with reliable source and we recommend jobs mainly based on the implicit feedbacks from users. According to the user’s behavior such as browsing time and search history, plus our own job similarity algorithm our website will give recommendations for similar job positions and reduce the interruption to lowest. We want to give user the ultimate experience when browsing our site. This is done by eliminating any ads and collecting data implicitly, which solves problems existed in other websites. Therefore, our project is really useful for people who want to find jobs.</span>

#### Regarding data

<span>The original data are from the glassdoor website and there is no available formatted data (they were embedded in HTML).</span> We designed a robust information collection system to simulate browsing, interact with webpage and parse corresponding HTML elements and store the data we need in MySQL database. First we parsed the web page and extracted only the job description related html and company html, stored them into a temporary dictionary and inserted into our job_unclean and company_unclean table. Then we formated the job description and company information using string processing and discard job with malformed job titles and other attributes and jobs without company source. Cleaned results were then stored into new tables. In total, we have 24000 jobs and 12000 companies in our database. Before publishing, for test purpose, we generated more than 10 fake users by creating job seekers and headhunters manually. However, all the other data is real data.

#### Initial plan

<span style="color: rgb(0,0,0);">Our initial plan was to build a job search website which allow users to post or search jobs, and we have achieved our goal. Users can identify themselves as job seekers or headhunters. The basic functions in our project allow job seekers to search for job or internship based on multiple criteria. It also helps headhunters to post or delete the jobs they’ve posted. Our website provide users with comprehensive job descriptions of the job positions that they are interested in. Based on user’s behavior, the recommendation system will send out emails of new job opportunities regarding similar positions. This is a functionality that we didn’t plan to do before.</span>

#### ER diagram

<span><span>![](https://lh3.googleusercontent.com/8e92I62iEC6O2wucZ_bB7ujs10_z1-TmQy2wk6-u-445936PV1i5OfzHDbqEaysV7_QWpfch52mLvHvlrKqqUPNus9p94ZV9omoV6VlzEVC2KkdQ7_6-KsRbOaiYxtTBFipMKxdk)</span></span>

#### Schema

user (<u>user_id</u>, email, username, usertype)

jobseeker (<u>user.user_id</u>, major, GPA, university, graduation_date, salary_expectation, image, personal_summary, bags_of_words_repr)

headhunter (<u>user.user_id</u>, image, synopsis, occupation_direction)

company (<u>company_id</u>, company_name, headquarters, industry, size, revenue, website, founded, type, sector, competitors, logo)

job (<u>job_id</u>, company.company_id, salary, job_title, work_status, location, job_description, posted_time, headhunter.user_id, bags_of_words_repr)

job_category (<u>category_name</u>, crawled)

proxies (ip, port, location, last_checked)

user_agents (agent, os)

browse_time (job_id, user_id, start_time, end_time, time_elapsed)

search_history (user_id, search_time, job_title, company_name, industry, location)

interest_job (user_id, job_id, recommended)

behavior_job (user_id, job_id, recommended)

crawler_system_loggings (<u>crawl_id</u>, start_time, end_time, logging_file_path, in_progress, succeeded)

## Data Collection

<span><span>For real job information data, we used Requests, Selenium and Pandas to collect and clean company data. We first crawled proxy and agent to help hide crawler’s identity. Then crawled the job and company data from glassdoor. Then stored the data in a temporary database and then batch cleaned these data and store them in our main database. For user-side data, we first faked a few users to simulate jobseekers and job hunters. After that, we deployed our app on the cloud and called friends and classmates to play with it so we could have some real data. User behavior data (event tracking) was collected behind the scene when users was browsing our site. For this, we used Javascript with Ajax to send frontend data to the backend.</span></span>

<span><span>  
</span></span>

## Feature Specs

<span>1\. User System (two types of users: job seeker(find jobs) / headhunter(post jobs), can be chosen at registration page)</span>

1.  <span>Sign up</span>

2.  <span>Sign in</span>

3.  <span>Sign out</span>

4.  <span>View profile (job seeker and headhunter have different profile attributes)</span>

5.  <span>Update profile (change profile image, upload personal information)</span>

<span>2\. Job Info System</span>

1.  <span>Automated & multithreading crawler (crawl real data from other job finding websites, behind the scene)</span>

2.  <span>Data cleaner (clean data for use, behind the scene)</span>

3.  <span>Post jobs (headhunter can post job information)</span>

4.  <span>View posted jobs (headhunter can view jobs they posted)</span>

5.  <span>Delete posted jobs (headhunter can delete jobs they posted)</span>

6.  <span>Search jobs (search all jobs from the database with any specification)</span>

<span>3\. Recommendation System</span>

1.  <span>Data parsing (behind the scene)</span>

2.  <span>Similarity Matching (behind the scene)</span>

3.  <span>Automatically send recommended jobs via email</span>

## Basic Code/Function Detail

#### One basic function

<span><span>Headhunters can view and delete jobs they’ve posted. The interface related to this function lies in the user profile page and is only visible for users who declared to be a headhunter when signing up. The view will perform a search in the database, and the deletion will generate a confirmation window before deleting it from the database.</span></span>

#### SQL code snippet

1. Search job
```SQL
select * from job as j
inner join company as c on c.company_id = j.company_id
where lower(j.job_title) like "%{job_title}%"
and j.location like "%{location}%"
and c.company_name like "%{company_name}%"and c.industry like "%{industry}%"
order by j.job_id, j.location, c.industry, c.company_id asc
limit {maximum_job_return}
```

2. Count the frequency of a keyword in a job search</span>
```SQL
INSERT INTO search_history (user_id, search_keyword, count)
VALUES ('{uid}', '{row[0]}', '{row[1]}')
ON DUPLICATE KEY UPDATE count = count + {row[1]}
```

3. Select jobs that are browsed for a long time</span>
```SQL
SELECT job_id, job_title
FROM (((SELECT job_id, sum(time_elapsed) as total_time
FROM browse_time WHERE user_id = '{uid}'
GROUP BY job_id
HAVING total_time >= {threshold}) as atable natural join job) natural join company)
```
#### Simplified Dataflow

<span style="color: rgb(0,0,0);"></span><span>A new user is able to create a new account with a username, password, email address and identity(job seeker or headhunter) and these information will be stored in our database. After creating the account, the user is able to sign in with username and password.</span>

<span>![](https://lh5.googleusercontent.com/86zBb6gT0rO8RqNvTqik64edYX-vJu4LSYtPkkwmHVQA1a1Dg51YUY1Sv2QcDsgNdm-I1CsI6Tx9L4P03pOZOkDwE3QgJvtCebDLTHTQXnqC05pILzEi4TgW0PgZDzvN6-hm4pYa)---login--->![](https://lh5.googleusercontent.com/X3josxtscOP-KFoHPllxa3GMSkYlXaFx20W02TfwMwmtBzrF-hIYPEc5tXQ_HHNI47fJcGAJYKIC16rBkI7ZhrAdtbn39A6soQQtZV1W-Gj0kVOUE0fXXzQO2lOmr2bpStk30gR3)</span>

<span>User can then search job opportunity on our website by typing into search bar. When clicked, each of the icons will pop up the detail job description information.</span>

![](https://lh3.googleusercontent.com/OcKgg0YI1XphDTb5tJ5OYB-UzvO4A-r0FZ1KR5VRpOfec3GDeQUXX0HdGzk4OTHLTbd3qfzKIxnJ9lt0ANFgWhdTHWcUJ7ooIc-iFyCLlr_ry2Tj5Xxuo2kD5rTLk_FGjprUuRLZ)---icon-clicked---> ![](https://lh4.googleusercontent.com/SszIj74vGBTtohPWuXU1BuXMYIqzYUwHRpo0IFUxdxIOAJUkg_Qh94u5qyH3pVYXvD-ZTLa3QKhOSIXh0LCqmztR2vmYUQxaqZZ6wj08jynFOtCfW9zVfh8ny7orvcKhlIC6uFTP)

<span>In general, by submitting these forms, the program will find the corresponding function in views.py from urls.py to process the request. The output will also be rendered by this function, passing back to frontend.</span>

<span>  
</span>

## <span>Advanced Functions</span>

### <span>Automated Crawler System</span>

<span style="color: rgb(0,0,0);">![](https://lh3.googleusercontent.com/0m10V3rhxF5UL6XClsJ6bsbd_Df_yUatRrVoAuhX8sGXhxApFtEy_D_Udz9vYg_n_NRkn7fjindFH2SADisyudfFlpLnXsAXM54xN_3oGguOQnVq2JI5o2FXgPCkwW87mxp3s1jz)</span>

<span>This our self-designed auto-information collection system. The above diagram shows the data flow of our crawler system. The company cleaned data, job cleaned data and full company logos are the final data we collected. Our information auto collection system is completely automated, from crawling to data cleaning. With one command, python</span> <span style="color: rgb(0,0,0);">Auto_collection_system.py, our system will run weekly at Wednesday, update our job and company database. Additional information will be recorded in our system’s logging file which serves as an archive for sanity check afterward. This system ensures our database always up to date which is crucial for job seekers.</span>

##### <span style="color: rgb(0,0,0);">_<span style="color: rgb(128,0,0);">Advanced</span> features:_</span>

*   <span>Multiprocessing & multithreading speed up</span>

*   <span>Rotate auto collected proxy and user agent to hide identity, not afraid of anti-crawler</span>

*   <span>Can catch asynchronous data</span>

*   <span>Catch pop-up ads and close them</span>

*   <span>Logging system</span>

##### _<span style="color: rgb(0,0,0);">Technical challenges and our Solutions:</span>_

*   <span>Information on websites is loaded only when the corresponding click event happens.</span>

    1. Use selenium to simulate explorer and interact with the website to get data

*   <span>Sometime crawler dies! Because ads will pop up after a certain time</span>
    1.  Detect the visibility of ads elements
    2.  Automatically close ads

*   <span>Crawling speed is too slow.</span>

    1.  <span>Use multithreading and multiprocessing</span>
        1.  20 threads for company logo crawler -> 20 times faster
        2.  4 process, parallelly simulate browsers and crawl job data -> 4 times faster
    2.  <span>Synchronization</span>
        1.  Use the MySQL database as tracker if each job is crawled
        2.  Pipelining the crawler

*   <span>Anti-crawling system banned our ip address!</span>

    1.  <span>First, crawl some proxies and user agents and store them in the database for later use</span>
    2.  Rotate proxies and user agents in combination to hide identity, automatically switch to another proxy when not working

##### <span style="color: rgb(0,0,0);">_Creativeness_:</span>

*   <span>Completely self-designed crawling system.</span>

*   <span>Automated crawler with logging. With one command, the whole system will pipeline itself and collect data.</span>

*   <span>Every crawler is different! They are designed for different web pages. But they also built upon each other to aid our main crawler. For example, the ip address crawler and the user agent crawler help with the rotation in the main crawler. We made our crawler even more distinct by implementing auto collection.</span>

##### <span style="color: rgb(0,0,0);">_Detailed explanation of the structure of our collection system:_</span>

*   <span style="color: rgb(0,0,0);">Auto_collection_system.py:</span>  
    The head of automatic information collection system, control job_title crawler, glassdoor crawler, IP crawler, logo crawler & agent crawler and record system loggings
*   <span style="color: rgb(0,0,0);">Crawl_job_titles.py:</span>  
    Crawl the most popular 700 careers, which will be used as a search query in glassdoor_crawler.
*   <span style="color: rgb(0,0,0);">Glassdoor_crawler.py:</span>  
    Collect job and company information by simulating itself as a browser. Support multi-processing crawling.
*   <span style="color: rgb(0,0,0);">Ip_address_crawler.py:</span>  
    Collect available free proxy that other crawler can use to hide their identity.
*   <span style="color: rgb(0,0,0);">Logo_crawler.py:</span>  
    Crawl all the logos of companies. Used multithreading to accelerate to 20 times speed.
*   <span style="color: rgb(0,0,0);">User_agent_crawler.py:</span>  
    Crawl all good agent for another crawler to use.

### <span>Content-based Recommendation System</span>

<span style="color: rgb(0,0,0);">To further help users find their satisfactory jobs, we designed our own recommendation system. Our system detects user behavior and collects data silently, reducing the noise to lowest. Our own recommendation system utilized NLP to extract technical terms from job description and user profile, then use KNN algorithm to find the best match for our users. Finally, we send color HTML email to users to help them identify their potential interested jobs.</span>

##### _<span style="color: rgb(0,0,0);">A</span><span style="color: rgb(133,32,12);">dvanced</span> <span style="color: rgb(0,0,0);">features:</span>_

*   <span>Implemented an NLP algorithm in paper based on sentence syntax to extract technical terms. Much better result for a recommendation</span>

*   <span>Adapted content-based recommendation system. Incorporate cosine similarity method with our pre-processed bags of word representation</span>

*   <span>Send HTML email with image and color, which is our way of pushing results to users</span>

##### _<span style="color: rgb(0,0,0);">Technical challenges and our Solutions:</span>_

*   <span>The initial result of calling sklearn and find the nearest job does not give the most related jobs.</span>

    1.  <span>Improve the result by extracting the technical terms instead of all terms.</span>
    2.  Implement an NLP algorithm based on a published paper to extract technical terms - significant better result

*   <span>Drastic loss of style when sending HTML email, we need to try hundreds of time to see if a certain style works in the email. Things sent by gmail server are not that stable, so we worked on it for days to get a beautiful email sent.</span>

    1.  We find the most stable method is to write Inline CSS.

##### _<span style="color: rgb(0,0,0);">Creativeness:</span>_

*   <span>When calculating similarity, we considered multiple aspects. Besides parsing personal summary, we implemented the modern concept of event tracking, which includes recording of search history and how much time a user stays on a particular job page. Normally a website would ask users to fill out their interests in a web form, such as to fill a personal summary. However in our website, in addition to this, we collect user behavior data implicitly, which is very creative. Instead of using third-party API, we used javascript in combination with ajax to accomplish this behavior tracking functionality by ourselves. These implicit user behaviors can help improve the precision of recommendation to some extent.</span>

*   <span>Delivering all information via a website seems boring. That’s why we decided to use a more creative way to show the recommended jobs to users, which is to automatically send a HTML email flyer after user browses our site. These emails are really powerful because we gain access to users even when they’re offline. We are able to reach them and provide valuable job information that may bring them back to our site right away. This functionality makes the recommendation system more effective and reachable to our users.</span>

##### <span style="color: rgb(0,0,0);">_Detailed explanation of the structure of our recommendation system:_</span>

*   <span style="color: rgb(0,0,0);">Utils/justeson_Extractor.py:</span>  
    Implemented technical term extraction paper<span style="color: rgb(0,0,0);">.</span> <span style="color: rgb(0,0,0);">Use NLP technique to extract all the technical terms in a document. R</span>eference:<span style="color: rgb(17,85,204);">[https://brenocon.com/JustesonKatz1995.pdf](https://brenocon.com/JustesonKatz1995.pdf)</span>  
    <u>Key idea:</u> Technical terms have special pattern of syntactic relation. To be specific:  
    ![](https://lh4.googleusercontent.com/7lDz0clFN1wqWtUtwH0PIu5lNfjk0B5TFxx-2UE6cixzMTyEJ2MxE-CRp3ZJrTgoAlSs6g1XUleKCsXBDwbhyNZBGJaPryYUjlpMuMhhqjXThUGy7jC0GuByBTLeK7_e8jicPTFi)  
    A is an ADJECTIVE, but not a determiner.  
    N is a LEXICAL NOUN (i.e. not a pronoun).  
    P is a PREPOSITION.  
    The algorithm is intended to provide both high coverages of a text's technical terminology and high quality of the candidate terms extracted. Our implementation is based on a preference for coverage over quality, except when a substantial gain in quality can be attained by a minimal sacrifice of coverage.<span style="color: rgb(0,0,0);">  
    </span>
*   <span style="color: rgb(0,0,0);">Label_jobs.py:</span>  
    Table: job_bag_of_word_repr  
    For each job description document, extract its technical term with frequency. Store its technical bags of words representation in the database table job_bag_of_word_repr
*   <span style="color: rgb(0,0,0);">Label_users.py:</span>  
    Table: user_bag_of_word_repr  
    For each user self summary profile, extract the technical terms with frequency. Store the technical bags of words representation in the database table user_bag_of_word_repr
*   <span style="color: rgb(0,0,0);">Similarity_calculation.py:</span>  
    Use sklearn to build a KDtree data structure.  
    Calculate the cosine similarity between each job.  
    <u>Key idea:</u><span style="color: rgb(0,0,0);">Assign an index to all of the distinct words in our data and store them in a dictionary</span>  
    For every job description, build its corresponding frequency vector based on the dictionary.  
    Convert user’s search history into bag of words representation and calculate its cosine similarity with the predefined frequency vector and use nearest neighbor to find the top n most similar job<span style="color: rgb(69,69,69);"></span>
*   <span style="color: rgb(0,0,0);">recommendation/views.py:</span>  
    Select top n recommended jobs for a user.  
    Render it to a HTML with CSS style  
    Wrap it as an HTML and send it to user

## Technical Challenge

<span style="color: rgb(0,0,0);">We encountered lots of technical challenges when we were trying to build our robust crawler. Being able to use real data is really important for our applications, so we want to share some advice so that future teams can avoid being stuck at this point.</span>

<span style="color: rgb(0,0,0);">One of the challenging issues we want to talk about is that the information we wanted on the page was loaded only when the corresponding clicking event happens. This meant that we couldn’t simply parse a plain html file fetched by a single url because we wouldn’t get any useful data. To solve this problem, we used selenium to simulate the process as if there were a real person clicking the buttons. What it did was to fire up some number of Google Chrome browsers and to interact with the website until they get to every page where the data was located. In this way, we wouldn’t bother with any hidden data behind the web page. At the same time, with some ads detection functions, we solved another problem, which was the pop-up ads that interrupted our crawling process.</span>

<span>  
</span>

## <span>Division of Labor & Team Management</span>

<span>Our group has 2 backend developer and 2 front-end developer. We first divide our jobs into unrelated parts so that we can work parallelly. When it comes to integration parts, define standard API to communicate. To be specific, we define some API or helper function will return processed data and one focus on implement the function while others just assume the function exist and develop their parts on top of that.</span>

#### <span>Division of labor</span>

*   <span>Xingzhi</span><span>: Backend development, develop advanced function, auto-collection system, host and maintain our app on AWS.</span>

*   <span>Junfeng</span><span>: Backend development, develop User System, Post/View/Delete Job functions, event tracking/user behavior collection in Recommendation system, send email logic and functionality.</span>

*   <span>Danjin</span><span>: front-end designer and development, design web pages, develop recommendation system and NLP algorithm</span> <span style="color: rgb(33,33,33);">to make recommended jobs for users.</span>

*   <span>Chenyu</span><span>: Front-end designer and development, design web pages and email style functionality for recommendation system</span>

#### <span>Teamwork management</span>

*   <span>Active Online communication via Wechat</span>

*   <span>Weekly group meeting - First check individual progress then discuss our meeting goal. Dispatch work. Usually, we continue to code together for a few hours after meeting, this is our discussion time. In the discussion, First, we resolve problems teammates encouraged since the last meeting, then we focus on our own job but we also share our knowledge and help debug each other’s part when encountering new difficulties.</span>

*   <span>We used Git as our version control system. Each of us has a personal branch to work with. We first develop our own part on our develop branch. When it becomes mature, we first merge with each other's branch then merge with origin master. And finally, push to origin master. It’s essential to have a different development branch to resolve version conflict.</span>

<span>  
</span>
