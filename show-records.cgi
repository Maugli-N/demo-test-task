#!/usr/bin/perl

=Info
  Форма поиска сообщений почтового сервера,
  разобранных из файла его журнала и сохранённых
  в таблицы базы данных и вывод HTML результата

  Правила отбора записей в документе Task.pdf

  Автор: N.N.S.
  Версия от: 2024-08-15

  Входные параметры принимаются методом POST
      text  - имя файла с журналом почтового сервера
      where - флаг выбора таблицы для поиска записей,
              если активирован, поиск в таблице 'log',
              иначе поиск в таблице 'message'
  Выходные параметры
      STDOUT форма и результат поиска
=cut


use strict "vars";
use DBI;
use to_db;
use vars qw/$html_file $title/;

$|=1;

# HTML часть отображаемой формы
$html_file = 'show-records.data';
# Заголовок HTML формы
$title = 'Поиск записей по адресу почты';

main_proc ();

sub main_proc
{
  my ($html, $post, $action, $text, $where, $offset);

  # Отправляем заголовок успешного создания HTML страницы
  print "Status: 200 Ok.\nContent-type: text/html; charset=utf-8\n\n";

  # Загружаем HTML часть формы
  $html = load_html();

  # Загружаем распознанный POST запрос
  $post = get_params();

  $text = '';
  if (exists($$post{'text'}))
  {
    $text = str_2_hidden($$post{'text'});
  }
  $where = '';
  if (exists($$post{'where'}))
  {
    $where = ' checked';
  }
  $offset = 0;
  if (exists($$post{'offset'}))
  {
    $offset = $$post{'offset'};
  }

  $action = $ENV{'SCRIPT_NAME'};
  $html =~ s/\%ACTION\%/$action/gs;
  $html =~ s/\%WHERE\%/$where/gs;
  $html =~ s/\%TITLE\%/$title/gs;
  $html =~ s/\%TEXT\%/$text/gs;
  print $html;

  # Вывод найденных по адресу почты записей
  show_records($$post{'text'}, exists($$post{'where'}), $offset);

  print "</body>\n</html>\n";

  return 0;
}

sub show_records
{
  my ($dbh, $sth, $text, $where, $records, $count, $cnt, $row);
  my ($offset, $search, $timestamp, $log_record, $page, $pages);
  $text = shift;
  $where = shift;
  $offset = shift;

  $search = $text;
  $search =~ s/^\s+//;
  $search =~ s/\s+$//;
  $search =~ s/([\'\%])/\\$1/gs;

  if ($text eq '') { return; }

  if ($where)
  {
    # SQL запросы количества записей, удовлетворяющих
    # условию поиска, и первых 100 таких записей из
    # таблицы 'log'
    $count = <<LOG_ONLY_CNT;
    SELECT COUNT(int_id) AS cnt
      FROM log
     WHERE address LIKE '%$search%'
LOG_ONLY_CNT

    $records = <<LOG_ONLY_SQL;
    SELECT created, str
      FROM log
     WHERE address LIKE '%$search%'
  ORDER BY created, int_id
     LIMIT 100
    OFFSET $offset
LOG_ONLY_SQL

  }
  else
  {
    # SQL запросы количества записей, удовлетворяющих
    # условию поиска, и первых 100 таких записей из
    # таблицы 'message'
    $count = <<MESSAGE_CNT;
    SELECT COUNT(DISTINCT m.int_id) AS cnt
      FROM message AS m
      JOIN log AS l
     WHERE l.int_id = m.int_id
       AND address LIKE '%$search%'
MESSAGE_CNT

    $records = <<MESSAGE_SQL;
    SELECT m.created, m.str
      FROM message AS m
      JOIN log AS l
     WHERE l.int_id = m.int_id
       AND address LIKE '%$search%'
  GROUP BY m.int_id
  ORDER BY m.created, m.int_id
     LIMIT 100
    OFFSET $offset
MESSAGE_SQL

  }

=Debug
  print "<p>Records counter</p><pre>$count</pre>\n";
  print "<p>Records data</p><pre>$records</pre>\n";
=cut

  # Подключаемся к базе данных
  $dbh = to_db::connect;

  # Узнаём количество записей, удовлетворяющих условию поиска
  $sth = $dbh->prepare($count);
  $cnt = $sth->execute;
  $cnt += 0;
  $count = 0;
  if ($cnt)
  {
    $row = $sth->fetchrow_hashref;
    $count = $$row{'cnt'};
  }
  $sth->finish;

  if ($count == 0)
  {
    print "<p align=center>Для адреса '$text' записей не найдено</p>\n";
  }
  else
  {
    # Если записи были найдены, запрашиваем первые 100
    $sth = $dbh->prepare($records);
    $cnt = $sth->execute;
    $cnt += 0;
    if ($count > 100)
    {
      $pages = int($count / 100);
      $offset = ($offset / 100) + 1;
      if ($pages * 100 < $count) { $pages ++; }
      print "<p align=center>Найдено записей <span
                class=current>$count</span>, показаны <span
                class=current>$cnt</span>\n   &nbsp; Страницы:";
      foreach $page (1..$pages)
      {
        if ($page == $offset)
        {
          print "&nbsp; <span class=current>$page</span>\n";
        }
        else
        {
          print "&nbsp; <span class=another"
             . " onclick=\"set_offset('$page');\">$page</span>\n";
        }
      }
      print "</p>\n";
    }
    else
    {
      print "<p align=center>Найдено записей <span
                class=current>$count</span></p>\n";
    }

    # Вывод заголовка таблицы со списком найденных записей
    print <<TABLE_HEADER;
<table class=records align=center>
  <tr>
    <td>timestamp</td>
    <td>строка лога</td>
  </tr>
TABLE_HEADER

    while($row = $sth->fetchrow_hashref)
    {
      $timestamp = $$row{'created'};
      $log_record = str_2_html($$row{'str'});
      # Вывод очередной найденной записи
      print <<TABLE_RECORD;
  <tr>
    <td>$timestamp</td>
    <td>$log_record</td>
  </tr>
TABLE_RECORD
    }
    $sth->finish;
    print "</table>\n";
  }

  $dbh->disconnect;
}

sub get_params
{
  my ($request, @params, $data, $param, $value, $post);

  if ($ENV{'REQUEST_METHOD'} eq 'POST')
  {
    read (STDIN, $request, $ENV{'CONTENT_LENGTH'});
  }
  else
  {
    $request = $ENV{'QUERY_STRING'};
  }
  $request =~ s/\r//gs;
  $request =~ s/\s+$//;

  $post = {};
  @params = split(/&/, $request);
  foreach $data (@params)
  {
    ($param, $value) = split (/=/, $data, 2);
    $param =~ tr/+/ /;
    $param =~ s/%([0-9a-fA-F]{2})/pack("c",hex($1))/ge;
    $value =~ tr/+/ /;
    $value =~ s/%([0-9a-fA-F]{2})/pack("c",hex($1))/ge;
    if (exists($$post{$param}))
    {
      if (ref($$post{$param}) ne 'ARRAY')
      {
        $$post{$param} = [ $$post{$param} ];
      }
      push(@{$$post{$param}}, $value);
    }
    else
    {
      $$post{$param} = $value;
    }
  }

  return $post;
}

sub load_html
{
  my ($line, $text);
  $text = '';
  open (HTML_FILE, $html_file);
  while (defined ($line = <HTML_FILE>))
  {
    $text .= $line;
  }
  close (HTML_FILE);
  return $text;
}

sub str_2_hidden
{
  my $str = shift;
  $str =~ s/\&/\&amp\;/gs;
  $str =~ s/\"/\&quot\;/gs;
  $str =~ s/\</\&lt\;/gs;
  $str =~ s/\>/\&gt\;/gs;
  return $str;
}

sub str_2_html
{
  my $str = shift;
  $str =~ s/\</&lt;/gsi;
  $str =~ s/\>/&gt;/gsi;
  $str =~ s/\n/<br>\n/gsi;
  $str =~ s/  /&nbsp; &nbsp; /gsi;
  return $str;
}

1;