!fpm run -- -a -o ~/development/raidbin/raid_rows.csv ~/development/raidbin/whatever.txt
program raidprocess
  implicit none
  integer, parameter :: max_line = 32768
  character(len=:), allocatable :: content
  integer :: iunit, ios

  type :: RaidRow
    character(len=:), allocatable :: file_id
    character(len=:), allocatable :: abbreviation
    integer, allocatable :: room_times(:)
    integer :: nrooms
  end type RaidRow

  call process_command()

contains

  subroutine process_command()
    implicit none
    integer :: argc, i, argi
    character(len=1024) :: arg
    character(len=:), allocatable :: outfile
    character(len=:), allocatable :: fname
    character(len=:), allocatable :: filecontent
    type(RaidRow), allocatable :: rows(:)
    integer :: nrows
    logical :: append

    call get_command_argument(0, arg)
    argc = command_argument_count()
    if (argc < 1) then
      print *, 'you done messed up the parameters'
      stop
    end if

    outfile = 'raids_output.csv'
    append = .false.
    argi = 1

    if (.not. allocated(rows)) allocate(rows(0))
    nrows = 0

    do while (argi <= argc)
      call get_command_argument(argi, arg)
      select case (trim(arg))
      case ('-o')
        if (argi+1 > argc) then
          print *, 'you done messed up the parameters (-o output.csv)'
          stop
        end if
        call get_command_argument(argi+1, arg)
        outfile = trim(arg)
        argi = argi + 2
      case ('-a', '--append')
        append = .true.
        argi = argi + 1
      case default
        fname = trim(arg)
        if (len_trim(fname) == 0) then
          argi = argi + 1
          cycle
        end if
        filecontent = read_whole_file(trim(fname))
        if (len_trim(filecontent) == 0) then
          write(*,*) 'cant find the fiule?', trim(fname)
          argi = argi + 1
          cycle
        end if
        call parse_raids_in_file(trim(fname), filecontent, rows, nrows)
        argi = argi + 1
      end select
    end do

    if (nrows == 0) then
      write(*,*) 'cant find the raids'
    else
      call write_csv(outfile, rows, nrows, append)
      write(*,*) 'Wrote ', nrows, ' raid rows to ', trim(outfile)
    end if
    do i = 1, nrows
      if (allocated(rows(i)%room_times)) deallocate(rows(i)%room_times)
    end do
    if (allocated(rows)) deallocate(rows)

  end subroutine process_command
  function read_whole_file(path) result(txt)
    implicit none
    character(len=*), intent(in) :: path
    character(len=:), allocatable :: txt
    character(len=1024) :: line
    integer :: lun, iost
    character(len=:), allocatable :: accum

    accum = ''
    open(newunit=lun, file=path, status='old', action='read', iostat=iost)
    if (iost /= 0) then
      txt = ''
      return
    end if
    do
      read(lun,'(A)', iostat=iost) line
      if (iost /= 0) exit
      if (len_trim(accum) == 0) then
        accum = trim(line)
      else
        accum = trim(accum)//' '//trim(line)
      end if
    end do
    close(lun)
    txt = adjustl(accum)
  end function read_whole_file

  subroutine parse_raids_in_file(path, text, rows, nrows)
    implicit none
    character(len=*), intent(in) :: path, text
    type(RaidRow), allocatable, intent(inout) :: rows(:)
    integer, intent(inout) :: nrows
    integer :: pos, lentext, i
    integer :: arr_start, k
    integer :: ch
    character(len=32) :: tmpid
    character(len=:), allocatable :: file_id
    character(len=:), allocatable :: obj
    integer :: p, startobj, endobj, depth

    lentext = len_trim(text)
    if (lentext == 0) return
    call system_clock(count=ch)
    write(tmpid, '(I0)') ch
    file_id = trim(adjustl(tmpid))//'_'//trim(path)
    pos = index(text, '[')
    if (pos == 0) then
      pos = 1
    end if

    p = pos
    do
      startobj = 0
      do while (p <= lentext)
        if (text(p:p) == '{') then
          startobj = p
          exit
        end if
        p = p + 1
      end do
      if (startobj == 0) exit
      depth = 0
      endobj = 0
      do while (p <= lentext)
        if (text(p:p) == '{') then
          depth = depth + 1
        else if (text(p:p) == '}') then
          depth = depth - 1
          if (depth == 0) then
            endobj = p
            exit
          end if
        end if
        p = p + 1
      end do
      if (endobj == 0) exit
      obj = text(startobj:endobj)
      call parse_single_raid(obj, file_id, rows, nrows)
      p = endobj + 1
    end do

  end subroutine parse_raids_in_file

  subroutine parse_single_raid(obj, file_id, rows, nrows)
    implicit none
    character(len=*), intent(in) :: obj, file_id
    type(RaidRow), allocatable, intent(inout) :: rows(:)
    integer, intent(inout) :: nrows
    integer :: posab, posch, pos, pos2, kvpos
    character(len=:), allocatable :: abbr
    character(len=:), allocatable :: challblock
    integer :: nkeys, i
    integer, allocatable :: keys(:)
    integer, allocatable :: times(:)
    integer :: keynum
    character(len=64) :: numbuf
    integer :: ierr
    integer :: startobj, endobj, depth, p
    character(len=:), allocatable :: kvobj
    integer :: t

    abbr = ''
    posab = index(obj, '"abbreviation"')
    if (posab == 0) posab = index(obj, '"abbrev"')
    if (posab == 0) posab = index(obj, '"name"')
    if (posab /= 0) then
      pos = index(obj(posab:), ':')
      if (pos > 0) then
        pos = posab + pos - 1
        pos2 = index(obj(pos:), '"')
        if (pos2 > 0) then
          pos2 = pos + pos2 - 1
          pos = index(obj(pos2+1:), '"')
          if (pos > 0) then
            pos = pos2 + pos
            abbr = obj(pos2+1:pos-1)
            abbr = trim(adjustl(abbr))
          end if
        end if
      end if
    end if

    if (abbr == '') abbr = '(unknown)'

    posch = index(obj, '"challenges"')
    if (posch == 0) then
      return
    end if
    pos = index(obj(posch:), '{')
    if (pos == 0) return
    pos = posch + pos - 1
    p = pos
    depth = 0
    endobj = 0
    do while (p <= len_trim(obj))
      if (obj(p:p) == '{') then
        depth = depth + 1
      else if (obj(p:p) == '}') then
        depth = depth - 1
        if (depth == 0) then
          endobj = p
          exit
        end if
      end if
      p = p + 1
    end do
    if (endobj == 0) return
    challblock = obj(pos:endobj)

    nkeys = 0
    allocate(keys(0))
    allocate(times(0))
    p = 1
    do
      kvpos = index(challblock(p:), '"')
      if (kvpos == 0) exit
      kvpos = p + kvpos - 1
      kvpos = kvpos + 1
      numbuf = ''
      do while (kvpos <= len_trim(challblock) .AND. &
         &   ichar(challblock(kvpos:kvpos)) >= ichar('0') .AND. &
         &   ichar(challblock(kvpos:kvpos)) <= ichar('9'))
        numbuf = trim(numbuf) // challblock(kvpos:kvpos)
        kvpos = kvpos + 1
        if (len_trim(numbuf) >= 60) exit
      end do
      if (len_trim(numbuf) == 0) then
        p = p + 1
        cycle
      end if
      read(numbuf, *, iostat=ierr) keynum
      if (ierr /= 0) then
        p = p + 1
        cycle
      end if

      pos = index(challblock(kvpos:), '{')
      if (pos == 0) then
        p = kvpos
        cycle
      end if
      startobj = kvpos + pos - 1
      depth = 0
      endobj = 0
      do
        if (startobj > len_trim(challblock)) exit
        if (challblock(startobj:startobj) == '{') then
          depth = depth + 1
        else if (challblock(startobj:startobj) == '}') then
          depth = depth - 1
          if (depth == 0) then
            endobj = startobj
            exit
          end if
        end if
        startobj = startobj + 1
      end do
      if (endobj == 0) then
        p = kvpos
        cycle
      end if
      kvobj = challblock(kvpos:endobj)

      t = extract_room_time(kvobj)

      nkeys = nkeys + 1
      call append_int(keys, nkeys, keynum)
      call append_int(times, nkeys, t)

      p = endobj + 1
    end do

    if (nkeys >= 4) then
      call sort_pairs(keys, times, nkeys)
      nrows = nrows + 1
      call append_row(rows, nrows)
      rows(nrows)%file_id = file_id
      rows(nrows)%abbreviation = abbr
      rows(nrows)%nrooms = nkeys
      allocate(rows(nrows)%room_times(nkeys))
      do i = 1, nkeys
        rows(nrows)%room_times(i) = times(i)
      end do
    end if

    if (allocated(keys)) deallocate(keys)
    if (allocated(times)) deallocate(times)

  end subroutine parse_single_raid

  function extract_room_time(obj) result(tval)
    implicit none
    character(len=*), intent(in) :: obj
    integer :: tval
    integer :: pos
    integer :: ierr2
    character(len=256) :: num
    character(len=256) :: numdigits, fullnum
    logical :: neg
    integer :: p, colon_pos, startpos
    tval = 0
    pos = index(obj, '"roomTotalTime"')
    if (pos /= 0) then
      pos = index(obj(pos:), ':')
      if (pos /= 0) then
        pos = pos + index(obj, '"roomTotalTime"') - 1
        pos = pos + pos - index(obj(pos:), ':') + 1
      end if
    end if
    tval = 0
    pos = index(obj, 'roomTotalTime')
    if (pos == 0) pos = index(obj, '"roomTotalTime"')
    if (pos /= 0) then
      colon_pos = index(obj(pos:), ':')
      if (colon_pos > 0) then
        startpos = pos + colon_pos
        p = startpos
        do while (p <= len_trim(obj) .AND. &
     &      (obj(p:p) == ' ' .OR. obj(p:p) == CHAR(9) .OR. &
     &       obj(p:p) == CHAR(10) .OR. obj(p:p) == CHAR(13)))
          p = p + 1
        end do
        numdigits = ''
        neg = .false.
        if (p <= len_trim(obj) .and. obj(p:p) == '-') then
          neg = .true.
          p = p + 1
        end if
        do while (p <= len_trim(obj) .and. ichar(obj(p:p)) >= ichar('0') .AND. ichar(obj(p:p)) <= ichar('9'))
          numdigits = trim(numdigits)//obj(p:p)
          p = p + 1
        end do
        if (len_trim(numdigits) > 0) then
          if (neg) then
            fullnum = '-'//trim(numdigits)
          else
            fullnum = trim(numdigits)
          end if
          read(fullnum, *, iostat=ierr2) tval
          if (ierr2 == 0) return
        end if
      end if
    end if

    tval = 0
  end function extract_room_time

  subroutine append_int(arr, n, val)
    implicit none
    integer, allocatable, intent(inout) :: arr(:)
    integer, intent(in) :: n, val
    integer, allocatable :: tmp(:)
    if (.not. allocated(arr)) then
      allocate(arr(1))
      arr(1) = val
      return
    end if
    allocate(tmp(size(arr)+1))
    tmp(1:size(arr)) = arr
    tmp(size(arr)+1) = val
    deallocate(arr)
    allocate(arr(size(tmp)))
    arr = tmp
    deallocate(tmp)
  end subroutine append_int

  subroutine append_row(rows, n)
    implicit none
    type(RaidRow), allocatable, intent(inout) :: rows(:)
    integer, intent(in) :: n
    type(RaidRow), allocatable :: tmp(:)
    integer :: oldn, newn
    newn = n
    if (newn < 1) return
    if (.not. allocated(rows)) then
      allocate(rows(newn))
      return
    end if
    oldn = size(rows)
    allocate(tmp(newn))
    if (oldn > 0) then
      tmp(1:oldn) = rows(1:oldn)
    end if
    deallocate(rows)
    allocate(rows(newn))
    rows = tmp
    deallocate(tmp)
  end subroutine append_row

  subroutine sort_pairs(keys, vals, n)
    implicit none
    integer, intent(inout) :: keys(:)
    integer, intent(inout) :: vals(:)
    integer, intent(in) :: n
    integer :: i, j, tkey, tval
    do i = 1, n-1
      do j = i+1, n
        if (keys(i) > keys(j)) then
          tkey = keys(i); keys(i) = keys(j); keys(j) = tkey
          tval = vals(i); vals(i) = vals(j); vals(j) = tval
        end if
      end do
    end do
  end subroutine sort_pairs

  subroutine write_csv(outfile, rows, nrows, append_in)
    implicit none
    character(len=*), intent(in) :: outfile
    type(RaidRow), intent(in) :: rows(:)
    integer, intent(in) :: nrows
    logical, intent(in) :: append_in
    integer :: i, j, maxrooms
    integer :: lun, ios
    logical :: existsf
    character(len=:), allocatable :: header, row

    maxrooms = 0
    do i = 1, nrows
      if (rows(i)%nrooms > maxrooms) maxrooms = rows(i)%nrooms
    end do

    inquire(file=outfile, exist=existsf)
    if (append_in .and. existsf) then
      open(newunit=lun, file=outfile, status='old', position='append', action='write', iostat=ios)
      if (ios /= 0) then
        write(*,*) 'Error opening output file for append: ', trim(outfile)
        return
      end if
    else
      open(newunit=lun, file=outfile, status='replace', action='write', iostat=ios)
      if (ios /= 0) then
        write(*,*) 'Error opening output file: ', trim(outfile)
        return
      end if
      header = 'file_id,abbreviation'
      do i = 1, maxrooms
        header = trim(header)//','//'room_'//trim(adjustl(itoa(i)))
      end do
      write(lun, '(A)') trim(header)
    end if

    do i = 1, nrows
      row = trim(rows(i)%file_id)//','//trim(escape_csv(rows(i)%abbreviation))
      do j = 1, maxrooms
        if (j <= rows(i)%nrooms) then
          row = trim(row)//','//trim(adjustl(itoa(rows(i)%room_times(j))))
        else
          row = trim(row)//','
        end if
      end do
      write(lun, '(A)') trim(row)
    end do
    close(lun)
  end subroutine write_csv

  pure function itoa(i) result(s)
    implicit none
    integer, intent(in) :: i
    character(len=32) :: s
    write(s, '(I0)') i
  end function itoa

  pure function escape_csv(sin) result(sout)
    implicit none
    character(len=*), intent(in) :: sin
    character(len=:), allocatable :: sout
    character(len=:), allocatable :: tmp
    integer :: n, i
    n = len_trim(sin)
    if (n == 0) then
      sout = ''
      return
    end if
    if (index(sin, ',') == 0 .AND. index(sin, '"') == 0) then
      sout = sin
      return
    end if
    tmp = ''
    do i = 1, n
      if (sin(i:i) == '"') then
        tmp = tmp//'""'
      else
        tmp = tmp//sin(i:i)
      end if
    end do
    sout = '"'//tmp//'"'
  end function escape_csv

end program raidprocess
