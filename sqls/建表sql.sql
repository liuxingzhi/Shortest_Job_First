-- User (user_id, password, email, username);   (FD: email-->user_id)
CREATE TABLE User
(
  user_id  INT          NOT NULL AUTO_INCREMENT,
  password VARCHAR(100) NOT NULL,
  email    VARCHAR(100) NOT NULL,
  username VARCHAR(100) NOT NULL,
  address  VARCHAR(100),
  phone    VARCHAR(100),
  nickname VARCHAR(100),
  PRIMARY KEY (user_id)
);

-- JobSeeker (User.user_id, major, GPA, university, graduation_date, salary_expectation);
CREATE TABLE JobSeeker
(
  user_id            INT          NOT NULL,
  major              VARCHAR(100) NOT NULL,
  GPA                FLOAT CHECK (GPA >= 0 AND GPA <= 4),
  university         VARCHAR(100),
  graduation_date    DATE,
  salary_expectation FLOAT,
  UNIQUE (user_id),
  FOREIGN KEY (user_id)
    REFERENCES User (user_id)
);

-- Headhunter (User.user_id, synopsis, occupation_direction);
CREATE TABLE Headhunter
(
  user_id              INT          NOT NULL,
  synopsis             VARCHAR(500) NOT NULL,
  occupation_direction VARCHAR(500) NOT NULL,
  UNIQUE (user_id),
  FOREIGN KEY (user_id)
    REFERENCES User (user_id)
);


-- Job (job_id, Company.company_name, job_title, location, salary, job_description, Headhunter.user_id);
CREATE TABLE Job
(
  job_id          INT NOT NULL,
  company_id      INT NOT NULL,
  salary          FLOAT,
  job_title       VARCHAR(100),
  location        VARCHAR(100),
  job_description VARCHAR(100),
  posted_time     VARCHAR(100),
  headhunter_id   INT,
  PRIMARY KEY (job_id),
  FOREIGN KEY (company_id)
    REFERENCES Company (company_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (headhunter_id)
    REFERENCES Headhunter (user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- Company (company_name, industry, scale, sales, country, website);   (FD: website-->company_name)
CREATE TABLE Company
(
  company_id   INT NOT NULL,
  company_name VARCHAR(100),
  headquarter  VARCHAR(100),
  industry     VARCHAR(100),
  scale        FLOAT,
  sales        FLOAT,
  country      VARCHAR(100),
  website      VARCHAR(100),
  PRIMARY KEY (company_id)
);


-- Favorite(JobSeeker.user_id, Job.job_id)
CREATE TABLE Favorite
(
  job_id  INT NOT NULL,
  user_id INT NOT NULL,
  FOREIGN KEY (job_id)
    REFERENCES Job (job_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (user_id)
    REFERENCES JobSeeker (user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);
