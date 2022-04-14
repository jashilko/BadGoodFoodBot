-- Table: public.users

-- DROP TABLE public.users;

CREATE TABLE IF NOT EXISTS public.users
(
    user_id integer NOT NULL,
    user_name character varying COLLATE pg_catalog."default",
    first_name character varying COLLATE pg_catalog."default",
    last_name character varying COLLATE pg_catalog."default",
    CONSTRAINT id PRIMARY KEY (user_id),
    CONSTRAINT user_id UNIQUE (user_id)
)

TABLESPACE pg_default;

ALTER TABLE public.users
    OWNER to knqprsizhfmhvo;


-- Table: public.categories

-- DROP TABLE public.categories;

CREATE TABLE IF NOT EXISTS public.categories
(
    id integer NOT NULL DEFAULT nextval('categories_id_seq'::regclass),
    name character varying(100) COLLATE pg_catalog."default",
    CONSTRAINT categories_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE public.categories
    OWNER to knqprsizhfmhvo;


-- Table: public.food_list

-- DROP TABLE public.food_list;

CREATE TABLE IF NOT EXISTS public.food_list
(
    id integer NOT NULL DEFAULT nextval('food_list_id_seq'::regclass),
    user_id integer,
    score smallint,
    descr character varying(200) COLLATE pg_catalog."default",
    foto_link character varying(500) COLLATE pg_catalog."default",
    date_add timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cat_id integer,
    CONSTRAINT food_list_pkey PRIMARY KEY (id),
    CONSTRAINT cat_id FOREIGN KEY (cat_id)
        REFERENCES public.categories (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT user_id FOREIGN KEY (user_id)
        REFERENCES public.users (user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE public.food_list
    OWNER to knqprsizhfmhvo;
-- Index: fki_cat_id

-- DROP INDEX public.fki_cat_id;

CREATE INDEX fki_cat_id
    ON public.food_list USING btree
    (cat_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: fki_user_id

-- DROP INDEX public.fki_user_id;

CREATE INDEX fki_user_id
    ON public.food_list USING btree
    (user_id ASC NULLS LAST)
    TABLESPACE pg_default;



-- Table: public.user_friends

-- DROP TABLE public.user_friends;

CREATE TABLE IF NOT EXISTS public.user_friends
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    user_id integer,
    friend_id integer,
    CONSTRAINT user_friend_pkey PRIMARY KEY (id),
    CONSTRAINT user_pair UNIQUE (user_id, friend_id),
    CONSTRAINT friend_id FOREIGN KEY (friend_id)
        REFERENCES public.users (user_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT user_id FOREIGN KEY (user_id)
        REFERENCES public.users (user_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)

TABLESPACE pg_default;

ALTER TABLE public.user_friends
    OWNER to knqprsizhfmhvo;