CREATE TABLE public.nowinteract
(
	date_time character(19),
	site_name character varying(8),
	posa_continent character varying(8),
	user_location_country character varying(8),
	user_location_region character varying(8),
	user_location_city character varying(8),
	orig_destination_distance double precision,
	user_id character varying(32),
	is_mobile integer,
	is_package integer,
	channel character varying(8),
	srch_ci date,
	srch_co date,
	srch_adults_cnt integer,
	srch_children_cnt integer,
	srch_rm_cnt integer,
	srch_destination_id integer,
	srch_destination_type_id character varying(8),
	is_booking integer,
	cnt integer,
	hotel_continent character varying(8),
	hotel_country character varying(8),
	hotel_market integer,
	hotel_cluster integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public.nowinteract
  OWNER TO "feng.zhao";

# Normalize the schema
ALTER table public.train Add column id character varying(32) NOT NULL DEFAULT '-1';
ALTER table public.train Add column set character varying(10) NOT NULL DEFAULT 'train';