-- Users
create table users (
    id uuid primary key references auth.users(id) on delete cascade,
    created_at timestamp with time zone default now()
);

-- Modules
create table modules (
    id serial primary key,
    title text not null,
    description text,
    "order" int not null,
    slug text unique not null
);

-- Blocks within a module (text, video, etc.)
create table module_blocks (
    id serial primary key,
    module_id int references modules(id) on delete cascade,
    "order" int not null,
    type text check (type in ('text', 'video', 'image', 'quiz_intro', 'code')),
    content jsonb not null
);

-- Questions for the module
create table questions (
    id serial primary key,
    module_id int references modules(id) on delete cascade,
    question_text text not null,
    type text check (type in ('single', 'multi', 'text', 'number')) not null,
    tolerance float, -- для числових питань
    exact_match boolean default true
);

-- Answers (for single/multi types)
create table answers (
    id serial primary key,
    question_id int references questions(id) on delete cascade,
    answer_text text not null,
    is_correct boolean not null
);

-- User answers to questions
create table user_answers (
    id serial primary key,
    user_id uuid references users(id) on delete cascade,
    question_id int references questions(id) on delete cascade,
    answer_text text not null,
    is_correct boolean,
    submitted_at timestamp with time zone default now()
);

-- Progress tracking for modules
create table progress (
    id serial primary key,
    user_id uuid references users(id) on delete cascade,
    module_id int references modules(id) on delete cascade,
    score float,
    passed boolean default false,
    completed_at timestamp with time zone
);

-- Certificates
create table certificates (
    id serial primary key,
    user_id uuid references users(id) on delete cascade,
    issued_at timestamp with time zone default now(),
    certificate_url text
);

-- Insert sample modules
INSERT INTO modules (title, description, "order", slug) VALUES
('Introduction to OSINT', 'Learn the fundamentals of open-source intelligence gathering and its applications.', 1, 'introduction-to-osint'),
('Search Engine Techniques', 'Master advanced search operators and techniques for efficient information discovery.', 2, 'search-engine-techniques'),
('Social Media Intelligence', 'Explore methods for gathering intelligence from social media platforms.', 3, 'social-media-intelligence'),
('Image and Video Analysis', 'Learn to extract metadata and verify multimedia content authenticity.', 4, 'image-video-analysis'),
('Domain and IP Investigation', 'Investigate websites, domains, and network infrastructure.', 5, 'domain-ip-investigation'),
('Digital Footprint Mapping', 'Create comprehensive profiles using publicly available information.', 6, 'digital-footprint-mapping'),
('Dark Web Intelligence', 'Safely navigate and gather intelligence from the dark web.', 7, 'dark-web-intelligence'),
('Threat Intelligence', 'Apply OSINT techniques for cybersecurity threat detection.', 8, 'threat-intelligence'),
('Legal and Ethical Considerations', 'Understand the legal framework and ethical boundaries of OSINT.', 9, 'legal-ethical-considerations'),
('Practical Case Studies', 'Apply your skills to real-world OSINT investigations.', 10, 'practical-case-studies');

-- Insert sample module blocks for first module
INSERT INTO module_blocks (module_id, "order", type, content) VALUES
(1, 1, 'text', '{"html": "<h2>Welcome to OSINT</h2><p>Open Source Intelligence (OSINT) is intelligence gathered from publicly available sources. This module will introduce you to the fundamental concepts and techniques.</p><p>Key topics covered:</p><ul><li>What is OSINT?</li><li>Legal and ethical considerations</li><li>Basic tools and techniques</li><li>Information verification</li></ul>"}'),
(1, 2, 'video', '{"url": "/Rickroll.mp4", "poster": "", "caption": "Example OSINT investigation walkthrough"}'),
(1, 3, 'quiz_intro', '{"description": "Test your understanding of basic OSINT concepts", "timeLimit": "10 minutes"}');

-- Insert sample module blocks for second module
INSERT INTO module_blocks (module_id, "order", type, content) VALUES
(2, 1, 'text', '{"html": "<h2>Advanced Search Operators</h2><p>Search engines are powerful tools for OSINT when used effectively. This module covers advanced techniques for precise information discovery.</p>"}'),
(2, 2, 'code', '{"code": "# Google Search Operators Examples\\nsite:example.com \\"confidential\\"\\nfiletype:pdf \\"annual report\\"\\nintitle:\\"index of\\" \\"passwords\\"\\ninurl:admin login\\n\\"email\\" AND \\"password\\" site:pastebin.com", "language": "bash"}'),
(2, 3, 'quiz_intro', '{"description": "Test your knowledge of search operators and techniques", "timeLimit": "15 minutes"}');

-- Insert sample questions for first module
INSERT INTO questions (module_id, question_text, type) VALUES
(1, 'What does OSINT stand for?', 'single'),
(1, 'Which of the following are OSINT sources? (Select all that apply)', 'multi'),
(1, 'Describe the importance of verifying information in OSINT investigations.', 'text');

-- Insert answers for first question
INSERT INTO answers (question_id, answer_text, is_correct) VALUES
(1, 'Open Source Intelligence', true),
(1, 'Online Security Intelligence Network', false),
(1, 'Operational System Intelligence Tool', false);

-- Insert answers for second question
INSERT INTO answers (question_id, answer_text, is_correct) VALUES
(2, 'Social media platforms', true),
(2, 'Public records', true),
(2, 'Classified documents', false),
(2, 'News websites', true);

-- Insert answers for third question
INSERT INTO answers (question_id, answer_text, is_correct) VALUES
(3, 'OSINT', true),

-- Insert sample questions for second module
INSERT INTO questions (module_id, question_text, type, tolerance) VALUES
(2, 'Which operator limits search results to a specific website?', 'single', null),
(2, 'How many Google search operators can you name?', 'number', 2);

-- Insert answers for second module questions
INSERT INTO answers (question_id, answer_text, is_correct) VALUES
(4, 'site:', true),
(4, 'domain:', false),
(4, 'url:', false),
(5, '15', true);
