
CREATE TYPE application_status AS ENUM (
'Applied',
'OA',
'Interview',
'Final Round',
'Rejected',
'Offer'
) ;


CREATE TABLE applications (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    status application_status NOT NULL,
    apply_date DATE NOT NULL DEFAULT CURRENT_DATE,
    job_url TEXT,
    location TEXT,
    pay TEXT,
    job_description TEXT
);


INSERT INTO applications(company, role, status)
VALUES
       ('META', 'SWE', 'Applied'),
       ('APPLE', 'SWE', 'Applied');

SELECT * FROM applications;