<#
    A Customizable Verse Text Widget

    Created by Couri (https://x.com/fncouri)

    !!*TEST BEFORE USING IN LIVE PROJECTS*!!
#>

using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /Verse.org/Colors }
using { /Verse.org/Colors/NamedColors }
using { /UnrealEngine.com/Temporary/UI }
using { /Verse.org/Assets }
using { /UnrealEngine.com/Temporary/SpatialMath }
using { /Fortnite.com/UI }

# Converts text justification to horizontal alignment
(InJustification : text_justification).ToHorizontalAlignment():horizontal_alignment=
    case(InJustification):
        text_justification.Left => horizontal_alignment.Left
        text_justification.Center => horizontal_alignment.Center
        text_justification.Right => horizontal_alignment.Right
        text_justification.InvariantLeft => horizontal_alignment.Left
        text_justification.InvariantRight => horizontal_alignment.Right

# Main class for custom texts
customizable_text_block := class():

    var DefaultText : string = ""
    var DefaultFontSize : float = 12.0
    var DefaultLineHeight : float = 12.0
    var DefaultLetterSpacing : float = 1.0
    var DefaultTextColor : color = White
    var DefaultShadowColor : color = Black
    var DefaultShadowOffset : ?vector2 = false
    var DefaultShadowOpacity : float = 0.0
    var DefaultJustification : text_justification = text_justification.Center

    var DisplayCanvas<private> : canvas = canvas{}
    var MainWidget<private> : stack_box = stack_box{Orientation := orientation.Vertical}


    # Sets the text to display
    SetText(InText : string):void=
        set DefaultText = InText
        UpdateDisplayText()

    GetText():string=
        return DefaultText

    # Sets the font size
    SetFontSize(InFontSize : float):void=
        set DefaultFontSize = InFontSize
        UpdateDisplayText()

    GetFontSize():float=
        return DefaultFontSize

    # Sets the line height
    SetLineHeight(InLineHeight : float):void=
        set DefaultLineHeight = InLineHeight
        UpdateDisplayText()

    GetLineHeight():float=
        return DefaultLineHeight

    # Sets the letter (horizontal) spacing
    SetLetterSpacing(InLetterSpacing : float):void=
        set DefaultLetterSpacing = InLetterSpacing
        UpdateDisplayText()

    GetLetterSpacing():float=
        return DefaultLetterSpacing

    # Sets the text color
    SetTextColor(InTextColor : color):void=
        set DefaultTextColor = InTextColor
        UpdateDisplayText()

    GetTextColor():color=
        return DefaultTextColor

    # Sets the shadow color
    SetShadowColor(InShadowColor : color):void=
        set DefaultShadowColor = InShadowColor
        UpdateDisplayText()

    GetShadowColor():color=
        return DefaultShadowColor

    # Sets the shadow offset
    SetShadowOffset(InShadowOffset : ?vector2):void=
        set DefaultShadowOffset = InShadowOffset
        UpdateDisplayText()

    GetShadowOffset():?vector2=
        return DefaultShadowOffset

    # Sets the shadow opacity
    SetShadowOpacity(InShadowOpacity : float):void=
        set DefaultShadowOpacity = InShadowOpacity
        UpdateDisplayText()

    GetShadowOpacity():float=
        return DefaultShadowOpacity

    # Sets the text justification
    SetJustification(InJustification : text_justification):void=
        set DefaultJustification = InJustification
        UpdateDisplayText()

    GetJustification():text_justification=
        return DefaultJustification

    # Creates the display text widget
    CreateDisplayText():stack_box=
        MainStackBox := stack_box{Orientation := orientation.Vertical}
        # Gets the number of lines in the text
        LineCount := GetLineCount(DefaultText)
        # Calculate base negative spacing based on font size and shadow
        var BaseNegativeSpacing : float = -1.0 * (DefaultFontSize / 1.75)  # Creates a negative base value
        var AdjustedLetterSpacing : float = DefaultLetterSpacing + BaseNegativeSpacing

        for:
            LineIndex := 0..LineCount
            LineContent := GetLineContent[DefaultText, LineIndex]
        do:
            # Create separate stack boxes for shadow and text
            TextLineBox := stack_box{Orientation := orientation.Horizontal}
            var FinalLineWidget : widget = TextLineBox

            # If shadow is enabled, create shadow line and overlay
            if(DefaultShadowOpacity > 0.0, ShadowOffset := DefaultShadowOffset?):
                ShadowLineBox := stack_box{Orientation := orientation.Horizontal}
                
                # Create characters for both shadow and text
                for:
                    CharIndex := 0..LineContent.Length
                    Char := LineContent[CharIndex]
                do:
                    # Create padding that varies based on character position
                    CharPadding := if (CharIndex = 0):
                        # First character only gets right padding
                        margin{Right := AdjustedLetterSpacing / 2.0}
                    else:
                        # Other characters get both left and right padding
                        margin{Left := AdjustedLetterSpacing / 2.0, Right := AdjustedLetterSpacing / 2.0}

                    ShadowLineBox.AddWidget(
                        stack_box_slot:
                            HorizontalAlignment := horizontal_alignment.Left
                            Padding := CharPadding
                            Widget := texture_block:
                                DefaultImage := Char.ToImage()
                                DefaultDesiredSize := vector2{X := DefaultFontSize, Y := DefaultFontSize}
                                DefaultTint := DefaultShadowColor
                    )
                    
                    TextLineBox.AddWidget(
                        stack_box_slot:
                            HorizontalAlignment := horizontal_alignment.Left
                            Padding := CharPadding
                            Widget := texture_block:
                                DefaultImage := Char.ToImage()
                                DefaultDesiredSize := vector2{X := DefaultFontSize, Y := DefaultFontSize}
                                DefaultTint := DefaultTextColor
                    )

                # Create overlay with shadow and text over each other
                set FinalLineWidget = overlay:
                    Slots := array:
                        overlay_slot:
                            HorizontalAlignment := horizontal_alignment.Fill
                            VerticalAlignment := vertical_alignment.Fill
                            Padding := margin{Left := ShadowOffset.X, Top := ShadowOffset.Y}
                            Widget := ShadowLineBox
                        overlay_slot:
                            HorizontalAlignment := horizontal_alignment.Fill
                            VerticalAlignment := vertical_alignment.Fill
                            Widget := TextLineBox
            else:
                # No shadow, just add text characters
                for:
                    CharIndex := 0..LineContent.Length
                    Char := LineContent[CharIndex]
                do:
                    # Create padding that varies based on character position
                    CharPadding := if (CharIndex = 0):
                        # First character only gets right padding
                        margin{Right := AdjustedLetterSpacing / 2.0}
                    else:
                        # Other characters get both left and right padding
                        margin{Left := AdjustedLetterSpacing / 2.0, Right := AdjustedLetterSpacing / 2.0}

                    TextLineBox.AddWidget(
                        stack_box_slot:
                            HorizontalAlignment := horizontal_alignment.Left
                            Padding := CharPadding
                            Widget := texture_block:
                                DefaultImage := Char.ToImage()
                                DefaultDesiredSize := vector2{X := DefaultFontSize, Y := DefaultFontSize}
                                DefaultTint := DefaultTextColor
                    )

            # Add the final line widget to main stack
            MainStackBox.AddWidget(
                stack_box_slot:
                    HorizontalAlignment := DefaultJustification.ToHorizontalAlignment()
                    Padding := margin{Bottom := DefaultLineHeight}
                    Widget := FinalLineWidget
            )

        
        return MainStackBox

    UpdateDisplayText():void=
        DisplayCanvas.RemoveWidget(MainWidget) # Remove the old widget
        NewDisplayText := CreateDisplayText() # Create the new widget
        set MainWidget = NewDisplayText # Keep a reference to the new widget
        DisplayCanvas.AddWidget(
            canvas_slot:
                Widget := MainWidget # Add the new widget
        )

    # Gets the widget, should be called anytime the widget is being added to a UI
    GetWidget():widget=
        UpdateDisplayText() # Update the display text
        return DisplayCanvas # Return the canvas
        
# Modified version of a split function that splits a string by line breaks
SplitString(InText : string, Separator : string)<transacts>:[]string=
    var FinalWords : []string = array{}
    var CurrentWord : string = ""

    for:
        Index := 0..InText.Length
        CurrentChar := InText[Index]
    do:
        if:
            CurrentChar = '\n'
        then:
            set FinalWords += array{CurrentWord}
            set CurrentWord = ""
        else:
            set CurrentWord = CurrentWord + "{CurrentChar}"
    
    # Add the last word if it's not empty
    if (CurrentWord.Length > 0):
        set FinalWords += array{CurrentWord}

    if(FinalWords.Length > 0):
        return FinalWords
    else:
        return array{InText} # Return the full text if no line breaks (when its a single line)

# Gets the number of lines in a string
GetLineCount(InText : string):int=
    return SplitString(InText, "\n").Length

# Gets the content of a specific line in a string
GetLineContent(InText : string, LineIndex : int)<transacts><decides>:string=
    return SplitString(InText, "\n")[LineIndex]


# --- CHARACTER MAPPING ---
#   !YOU WILL HAVE ERRORS IN THE SECTION BELOW AT FIRST!
#   
#   This is where you're supposed to paste the character mapping generated by the font tool!
#   *You may see error lines in the code below for a few second after adding the folder with the images
#   This is because the editor is still loading the images, just wait a few seconds and it should be fine*
# 

#Replace this with the character mapping generated by the font tool 
(InChar : char).ToImage():texture=
    case(InChar):
        _ => output.custom_font_L_space


#EXAMPLE USAGE - Creates the UI shown in the video

Custom_Verse_Font := class(creative_device):

    @editable StartTrigger : trigger_device = trigger_device{}

    # Runs when the device is started in a running game
    OnBegin<override>()<suspends>:void=
        StartTrigger.TriggeredEvent.Subscribe(OnTriggered)

    # Shows the test UI when triggered
    OnTriggered(MAgent : ?agent):void=
        if(Agent := MAgent?, Player := player[Agent]):
            spawn{ShowUI(Player)}

    #Creates a simple UI with just the custom text block in the center of the screen
    CreateUI(CustomTextBlock : customizable_text_block):canvas=
        canvas:
            Slots := array:
                canvas_slot:
                    Anchors := anchors{Minimum := vector2{X := 0.5, Y := 0.3}, Maximum := vector2{X := 0.5 , Y := 0.3}}
                    Alignment := vector2{X := 0.5, Y := 0.5}
                    Widget := CustomTextBlock.GetWidget() # Gets the custom text block widget

    ShowUI(Player : player)<suspends>:void=
        if(PlayerUI := GetPlayerUI[Player]):
            # Variables for changing text properties in a loop, not really needed for most use cases
            var CurrFontSize : float = 100.0
            var CurrLineHeight : float = 12.0
            var CurrLetterSpacing : float = 0.0
            var CurrTextColor : color = White
            var CurrShadowColor : color = Black
            var CurrShadowOffset : ?vector2 = option{vector2{X := 2.0, Y := 2.0}}
            var CurrShadowOpacity : float = 1.0

            # Creates the custom text block
            CustomTextBlock := customizable_text_block:
                DefaultText := "Custom Verse Text :)"
                DefaultFontSize := 100.0
                DefaultLineHeight := 12.0
                DefaultTextColor := Blue

            NewUI := CreateUI(CustomTextBlock) # Creates the UI
            PlayerUI.AddWidget(NewUI) # Adds the UI to the player


            Sleep(1.0)

            # --- Changing Font Size ---

            CustomTextBlock.SetText("With Custom font size!")
            loop:
                if(CurrFontSize >= 150.0):
                    break
                Sleep(0.1)
                set CurrFontSize += 1.0
                CustomTextBlock.SetFontSize(CurrFontSize)

            CustomTextBlock.SetFontSize(100.0)
            
            Sleep(1.0)

            # --- Changing Character Spacing ---

            CustomTextBlock.SetText("And character spacing!")
            loop:
                if(CurrLetterSpacing >= 35.0):
                    break
                Sleep(0.1)
                set CurrLetterSpacing += 1.0
                CustomTextBlock.SetLetterSpacing(CurrLetterSpacing)

            CustomTextBlock.SetLetterSpacing(0.0)


            # --- Changing Colors ---

            CustomTextBlock.SetText("And colors!")
            Sleep(0.5)
            CustomTextBlock.SetTextColor(Red)
            Sleep(0.5)
            CustomTextBlock.SetTextColor(Green)
            Sleep(0.5)
            CustomTextBlock.SetTextColor(Blue)
            Sleep(0.5)
            CustomTextBlock.SetTextColor(Pink)
            Sleep(1.0)
            CustomTextBlock.SetTextColor(White)

            Sleep(1.0)

            # --- Changing Shadows ---

            CustomTextBlock.SetText("even Shadows?!!")
            CustomTextBlock.SetShadowOffset(option{vector2{X := 2.0, Y := 2.0}})
            CustomTextBlock.SetShadowOpacity(1.0)
            CustomTextBlock.SetShadowColor(Black)
            Sleep(1.0)
            CustomTextBlock.SetShadowColor(Red)
            Sleep(1.0)
            CustomTextBlock.SetShadowColor(Green)
            Sleep(1.0)
            CustomTextBlock.SetShadowColor(Blue)
            Sleep(1.0)
            CustomTextBlock.SetShadowColor(Black)
            loop:
                if(CurrShadowOffset?.X >= 10.0):
                    break
                Sleep(0.15)
                if(CSH := CurrShadowOffset?):
                    NewVectorOffset := vector2{X := CSH.X + 1.0, Y := CSH.Y + 1.0}
                    set CurrShadowOffset = option{NewVectorOffset}
                    CustomTextBlock.SetShadowOffset(option{NewVectorOffset})


            Sleep(1.0)

            # --- Changing Line Height ---
            CustomTextBlock.SetShadowOffset(option{vector2{X := 2.0, Y := 2.0}})

            CustomTextBlock.SetText("Supports multiple lines!\nLike this!\n And this!")
            Sleep(2.0)
        
            CustomTextBlock.SetText("and different line heights!\nLine 1\nLine 2\nLine 3")

            loop:
                if(CurrLineHeight >= 30.0):
                    break
                Sleep(0.1)
                set CurrLineHeight += 1.0
                CustomTextBlock.SetLineHeight(CurrLineHeight)

            Sleep(1.0)

            CustomTextBlock.SetLineHeight(12.0)

            # --- Changing Text Justification ---

            CustomTextBlock.SetText("And different Justifications!\n Like Center\n Or Left\n Or Right")
            Sleep(2.0)
            CustomTextBlock.SetJustification(text_justification.Left)
            Sleep(2.0)
            CustomTextBlock.SetJustification(text_justification.Right)
            Sleep(2.0)
            CustomTextBlock.SetJustification(text_justification.Center)


            Sleep(2.0)
            CustomTextBlock.SetText("Link In Replies :)")
            CustomTextBlock.SetFontSize(300.0)
            CustomTextBlock.SetLetterSpacing(-10.0)
            CustomTextBlock.SetTextColor(Blue)
            CustomTextBlock.SetShadowColor(Red)
            CustomTextBlock.SetShadowOffset(option{vector2{X := 2.0, Y := 2.0}})
            CustomTextBlock.SetShadowOpacity(1.0)


            Sleep(6.0)
            PlayerUI.RemoveWidget(NewUI) # Removes the UI

