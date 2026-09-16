-- Called only with a unique temporary workbook created by export_excel_pdf.py.
-- Never activates Excel, changes app preferences, or quits the application.
on run argv
    if (count of argv) is not 3 then error "Expected input workbook, output PDF, and timeout."
    set inputPath to item 1 of argv
    set outputPath to item 2 of argv
    set eventTimeout to (item 3 of argv) as integer
    set oldDelimiters to AppleScript's text item delimiters
    set AppleScript's text item delimiters to "/"
    set inputName to last text item of inputPath
    set AppleScript's text item delimiters to oldDelimiters
    if inputName does not start with "resume-pdf-" then error "Only a generated temporary workbook can be exported."
    set outputHFS to (POSIX file outputPath) as text
    set trialBook to missing value
    set exportStep to "checking open workbooks"
    tell application "Microsoft Excel"
        with timeout of eventTimeout seconds
            log exportStep
            set openNames to name of every workbook
            if openNames is not missing value then
                if inputName is in openNames then error "Temporary workbook is already open; no workbook was changed."
            end if
            try
                set exportStep to "opening temporary workbook"
                log exportStep
                -- Standard Open Document works on versions where open workbook
                -- returns no object. Only the disposable copy is opened.
                open (POSIX file inputPath)
                if not (exists workbook inputName) then error "Excel did not open the temporary workbook. Check file access and workbook format."
                set trialBook to workbook inputName
                set exportStep to "reading temporary workbook sheets"
                log exportStep
                set sheetCount to count of worksheets of trialBook
                set exportStep to "saving temporary workbook as PDF"
                log exportStep
                save workbook as trialBook filename outputHFS file format PDF file format
                set exportStep to "closing temporary workbook"
                log exportStep
                close trialBook saving no
                return "PDF exported; worksheet count = " & sheetCount
            on error errorText number errorNumber
                -- Only the generated name is eligible for cleanup. The preflight
                -- guard above ensures an already-open user workbook is excluded.
                try
                    if trialBook is not missing value then
                        close trialBook saving no
                    else
                        set remainingNames to name of every workbook
                        if remainingNames is not missing value then
                            if inputName is in remainingNames then close workbook inputName saving no
                        end if
                    end if
                end try
                error exportStep & ": " & errorText number errorNumber
            end try
        end timeout
    end tell
end run
