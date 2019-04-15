-- User (user_id, password, email, username);   (FD: email-->user_id)
CREATE TABLE IF NOT EXISTS user
(
  user_id   INT          NOT NULL AUTO_INCREMENT,
  email     VARCHAR(100) NOT NULL,
  username VARCHAR(100) NOT NULL,
  address   VARCHAR(100),
  phone     VARCHAR(100),
  realname  VARCHAR(100) NOT NULL,
  usertype  int(11) NOT NULL DEFAULT 0,
  UNIQUE (user_id),
  PRIMARY KEY (user_id)
);

-- JobSeeker (User.user_id, major, GPA, university, graduation_date, salary_expectation);
CREATE TABLE IF NOT EXISTS jobseeker
(
  user_id            INT          NOT NULL,
  major              VARCHAR(100) NOT NULL,
  GPA                FLOAT CHECK (GPA >= 0 AND GPA <= 4),
  university         VARCHAR(100),
  graduation_date    int(11),
  salary_expectation VARCHAR(100),
  UNIQUE (user_id),
  FOREIGN KEY (user_id)
    REFERENCES user (user_id)
);

-- Headhunter (User.user_id, synopsis, occupation_direction);
CREATE TABLE IF NOT EXISTS headhunter
(
  user_id              INT          NOT NULL,
  synopsis             VARCHAR(500) NOT NULL,
  occupation_direction VARCHAR(500) NOT NULL,
  UNIQUE (user_id),
  FOREIGN KEY (user_id)
    REFERENCES user (user_id)
);

-- Company (company_name, industry, scale, sales, country, website);   (FD: website-->company_name)
CREATE TABLE IF NOT EXISTS company
(
  company_id   BIGINT(11),
  company_name VARCHAR(100),
  headquarters VARCHAR(200),
  industry     VARCHAR(100),
  size         VARCHAR(100),
  revenue      VARCHAR(100),
  website      VARCHAR(200),
  founded      VARCHAR(100),
  type         VARCHAR(100),
  sector       varchar(100),
  competitors  varchar(500),
  logo_path    varchar(300),
  logo_url     varchar(300),
  PRIMARY KEY (company_id)
);

CREATE TABLE IF NOT EXISTS company_data_unclean
(
  company_id   BIGINT(11),
  company_name VARCHAR(100),
  headquarters VARCHAR(200),
  industry     VARCHAR(100),
  size         VARCHAR(100),
  revenue      VARCHAR(100),
  website      VARCHAR(200),
  founded      VARCHAR(100),
  type         VARCHAR(100),
  sector       varchar(100),
  competitors  varchar(500),
  logo_path    varchar(300),
  logo_url     varchar(300),
  PRIMARY KEY (company_id)
);

-- Job (job_id, Company.company_name, job_title, location, salary, job_description, Headhunter.user_id);
CREATE TABLE IF NOT EXISTS job
(
  job_id               BIGINT(11),
  company_id           BIGINT(11),
  salary               VARCHAR(100),
  job_title            VARCHAR(100),
  location             VARCHAR(100),
  job_description      TEXT,
  job_description_html TEXT,
  posted_time          VARCHAR(100),
  headhunter_id        INT DEFAULT NULL,
  PRIMARY KEY (job_id),
  FOREIGN KEY (company_id)
    REFERENCES company (company_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (headhunter_id)
    REFERENCES headhunter (user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS job_data_unclean
(
  job_id               BIGINT(11),
  company_id           BIGINT(11),
  salary               VARCHAR(100),
  job_title            VARCHAR(100),
  location             VARCHAR(100),
  job_description      TEXT,
  job_description_html TEXT,
  posted_time          VARCHAR(100),
  headhunter_id        INT,
  PRIMARY KEY (job_id),
  FOREIGN KEY (company_id)
    REFERENCES company_data_unclean (company_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (headhunter_id)
    REFERENCES headhunter (user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- Favorite(JobSeeker.user_id, Job.job_id)
CREATE TABLE IF NOT EXISTS favorite
(
  job_id  BIGINT(11) NOT NULL,
  user_id INT          NOT NULL,
  FOREIGN KEY (job_id)
    REFERENCES job (job_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (user_id)
    REFERENCES jobseeker (user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS jobseeker_tags
(
  user_id INT          NOT NULL,
  tag     varchar(100) NOT NULL,
  FOREIGN KEY (user_id)
    REFERENCES jobseeker (user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS job_tags
(
  job_id BIGINT(11) NOT NULL,
  tag    varchar(100) NOT NULL,
  FOREIGN KEY (job_id)
    REFERENCES job (job_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS company_logo_downloaded
(
  company_id BIGINT(11) NOT NULL,
  downloaded  BOOL DEFAULT FALSE,
  PRIMARY KEY (company_id)
);

CREATE TABLE IF NOT EXISTS proxies
(
  ip VARCHAR(100),
  port VARCHAR(10),
  location VARCHAR(5),
  last_checked VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS user_agents
(
  agent VARCHAR(300),
  os VARCHAR(20)
);