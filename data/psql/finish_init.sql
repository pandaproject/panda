create or replace function exec(text) returns void as $$
begin
execute $1;
end;
$$ language plpgsql;

select exec('alter table '||table_name||' owner to panda') from information_schema.tables where table_schema='public';