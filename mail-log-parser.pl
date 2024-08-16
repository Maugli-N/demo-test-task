#!/usr/bin/perl -I.

=Info
  Программа разбора журнала почтового сервера и
  сохранения разобранного в таблицы базы данных

  Правила разбора журнала в документе Task.pdf

  Автор: N.N.S.
  Версия от: 2024-08-15

  Входные параметры
      $argv[0] - имя файла с журналом почтового сервера
  Выходные параметры
      STDOUT сообщение о количестве обработанных записей
=cut

use strict "vars";
use DBI;
use to_db;
use vars qw/$known_flags/;

$|=1;

# Известные типы флагов обработки почтовых сообщений
$known_flags =
{
  '<=' => 'прибытие сообщения (в этом случае за флагом'.
                             ' следует адрес отправителя)',
  '=>' => 'нормальная доставка сообщения',
  '->' => 'дополнительный адрес в той же доставке',
  '**' => 'доставка не удалась',
  '==' => 'доставка задержана (временная проблема)',
};

main_proc (@ARGV);

sub main_proc
{
  # Выделяем память под переменные;
  my ($dbh, $file, $message_sql, $log_sql, $message, $log);
  my ($line, $created, $id, $int_id, $str, $address, $flag);
  my ($msg, $result, $message_count, $log_count);
  
  $dbh = to_db::connect;
  $file = shift;

  # Проверяем наличие файла с журналом почтового сервера
  if (!(-f $file))
  {
    print "Not found mail log file '$file'\n";
    return 1;
  }

  $message_sql = <<MESSAGE_INSERT;
    INSERT IGNORE
      INTO message
           (created, id, int_id, str, status)
    VALUES (?, ?, ?, ?, 'FASLE')
MESSAGE_INSERT
  $log_sql = <<LOG_INSERT;
    INSERT
      INTO log
           (created, int_id, str, address)
    VALUES (?, ?, ?, ?)
LOG_INSERT
  $message = $dbh->prepare($message_sql);
  $log = $dbh->prepare($log_sql);

  # Открываем журнал почтового сервера на чтение
  open (MAILLOG, $file);
  # Обнуляем счётчики обработанных записей
  $message_count = 0;
  $log_count = 0;
  # Запускаем построчную обработку журнала
  while (defined ($line = <MAILLOG>))
  {
    # Удаялем символы пробелов и перевода
    # строки, обрамляющие считанную строку
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    if ($line eq '') { next; }

    # Считываем временную метку
    $created = substr($line, 0, 19);
    # Подготавливаем текст записи журнала для сохранения
    $str = substr($line, 20);
    # Считываем идентификатор обрабатываемого письма из 16 символов
    $int_id = substr($str, 0, 16);
    # Проверяем корректность идентификатора
    if ($int_id =~ /^[0-9A-Z]{6}-[0-9A-Z]{6}-[0-9A-Z]{2}$/i)
    {
      # Считываем флаг обработки письма
      $flag = substr($str, 17, 2);
      if (!(exists($$known_flags{$flag}))) { $flag = ''; }
      # Подготавливаем тескт для поиска адреса электронной почты
      if ($flag eq '')
      {
        $msg = substr($str, 17);
      }
      else
      {
        $msg = substr($str, 20);
      }
      $id = '';
      # Так как извлекать id нужно только для
      # сохранения в таблицу message и только
      # сообщений с флагом '<=', смотрим на
      # значение флага
      if ($flag eq '<=') {
        if ($msg =~ /\sid=([^\s]+)(\s|$)/) { $id = $1; }
      }
    }
    # При некорректноом идентификаторе устанавливаем его пустым
    else
    {
      $id = '';
      $flag = '';
      $int_id = '';
      $address = '';
      $msg = $str;
    }

    # Ищем адрес электронной почты
    if ($msg =~ /([^\s\<]+\@[^\s\>]+)/)
    {
      $address = $1;
    }
    else
    {
      $address = '';
    }

=Debug
    print "$created\t'$int_id'\t'$flag'\t<$address>\t$id\n";
=cut

    if (($id ne '') && ($int_id ne '') && ($flag eq '<='))
    {
      $result = $message->execute($created, $id, $int_id, $str);
      $message_count += $result;
    }
    $result = $log->execute($created, $int_id, $str, $address);
    $log_count += $result;
  }

  close (MAILLOG);
  
  $message->finish;
  $log->finish;
  $dbh->disconnect;

  print "Performed log records: $log_count\n";
  print "Saved message records: $message_count\n";

  return 0;
}

1;