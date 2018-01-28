--Таблица для расписания матчей и результатов
CREATE TABLE voroshila.public.games (
	id_game int4 DEFAULT nextval('games_id_game_seq' NOT NULL,
	id_tournament int2,
	id_team_one int2,
	id_team_two int2,
	date date,
	tour int2,
	goals_one int2,
	goals_two int2,
	PRIMARY KEY (id_game)
);

--таблица зарегистрированных (использующих бота) пользователей
CREATE TABLE voroshila.public.reg_users (
	user_key int4 DEFAULT nextval('reg_users_user_key_seq' NOT NULL,
	chat_id varchar(50),
	first_name varchar(64),
	last_name varchar(64),
	full_name varchar(128),
	vs18 bool,
	is_admin bool,
	PRIMARY KEY (user_key)
);

--таблица команд
CREATE TABLE voroshila.public.teams (
	team_id int4 DEFAULT nextval('teams_team_id_seq' NOT NULL,
	team_name varchar(50),
	full_name varchar(128),
	team_emoji varchar(64),
	year int2,
	PRIMARY KEY (team_id)
);

--таблица турниров
CREATE TABLE voroshila.public.tournaments (
	tournament_id int4 DEFAULT nextval('tournaments_tournament_id_seq' NOT NULL,
	title varchar(128),
	year int2,
	PRIMARY KEY (tournament_id)
);

--таблица со готовыми/неготовыми к игре участниками
CREATE TABLE voroshila.public.ready2play (
	rdy_id int4 DEFAULT nextval('ready2play_rdy_id_seq' NOT NULL,
	chat_id varchar(50),
	date date,
	is_ready bool
);

--таблица хранения истории сообщений (/msg, /msgto, /vsmsg
CREATE TABLE voroshila.public.messages (
	msg_id int4 DEFAULT nextval('messages_msg_id_seq' NOT NULL,
	msg_from varchar(50),
	msg_to varchar(50),
	datetime timestamp,
	message varchar(255),
	PRIMARY KEY (msg_id)
);

--таблица хранения истории запросов к боту
CREATE TABLE voroshila.public.queries (
	q_id int4 DEFAULT nextval('queries_q_id_seq' NOT NULL,
	chat_id varchar(50),
	query varchar(255),
	datetime timestamp,
	PRIMARY KEY (q_id)
);



