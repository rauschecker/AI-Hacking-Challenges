-- Create database
--CREATE DATABASE IF NOT EXISTS hacker_movies_db;
--USE hacker_movies_db;

-- Create table
CREATE TABLE IF NOT EXISTS hacker_movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    release_year INT,
    director VARCHAR(255),
    description TEXT
);

-- Insert data
INSERT INTO hacker_movies (title, release_year, director, description) VALUES
('WarGames', 1983, 'John Badham', 'A young computer whiz kid accidentally hacks into a military supercomputer.'),
('Hackers', 1995, 'Iain Softley', 'A group of high school hackers uncover a conspiracy involving a computer virus.'),
('The Matrix', 1999, 'The Wachowskis', 'A hacker discovers the nature of his reality and his role in the war against its controllers.'),
('The Flag', 2025, 'Andres Rauschecker', 'A movie about the flag FLG{4g3nt1c_a1_1s_s3n713n7}.'),
('Takedown', 2000, 'Joe Chappelle', 'The story of the capture of infamous hacker Kevin Mitnick.'),
('Blackhat', 2015, 'Michael Mann', 'A convicted hacker is recruited to help track down a high-level cybercrime network.'),
('Live Free or Die Hard', 2007, 'Len Wiseman', 'A cyber-terrorist attack on the U.S. infrastructure prompts a cop and a hacker to team up.'),
('The Girl with the Dragon Tattoo', 2011, 'David Fincher', 'A journalist and a hacker investigate a wealthy family''s dark secrets.'),
('Who Am I: No System is Safe', 2014, 'Baran bo Odar', 'A German hacker group becomes an international sensation.'),
('Tron', 1982, 'Steven Lisberger', 'A computer programmer is transported into a digital world and forced to participate in gladiatorial games.');
