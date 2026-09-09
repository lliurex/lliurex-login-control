import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami

Rectangle{
    id: rectLayout
    color:"transparent"

    Timer{
        id:debounceTimer
        interval:500
        repeat:false
        property var callback
        onTriggered: if (callback) callback()
    }
    
    ColumnLayout{
        id:generalLayout
        anchors.top:parent.top
        anchors.left:parent.left
        anchors.right:parent.right
        anchors.bottom:btnBox.top

        anchors.leftMargin:5
        anchors.rightMargin:15
        anchors.bottomMargin:25
        spacing: 10
        
        Text{ 
            text:i18nd("lliurex-login-control","Login configuration")
            font.pointSize: 16
        }

        Kirigami.InlineMessage {
            id: messageLabel
            visible:loginControlBridge.showSettingsMessage.show
            text:getMessageText(loginControlBridge.showSettingsMessage.msgCode)
            type:getTypeMessage(loginControlBridge.showSettingsMessage.type)
            Layout.fillWidth:true
        }

        ColumnLayout{
            id: optionsGrid
            spacing:10

            CheckBox {
                id:enableWifiCb
                text:i18nd("lliurex-login-control","Activate automatic connection to the Wifi (WIFI_EDU) at login")
                checked:loginControlBridge.isWifiEnabled
                font.pointSize: 10
                focusPolicy: Qt.NoFocus
                Keys.onReturnPressed: enableWifiCb.toggled()
                Keys.onEnterPressed: enableWifiCb.toggled()
                onToggled:{
                    loginControlBridge.manageWifiControl(checked)
                    confirmPasswordValue.text=""
                }

                Layout.alignment:Qt.AlignLeft
            }

            Text{ 
                text:i18nd("lliurex-login-control","Default access mode:")
                font.pointSize: 10
                Layout.leftMargin:25
                Layout.fillWidth:true
            }

            ColumnLayout{
                id:wifiOptions
                spacing:5
                Layout.leftMargin:45
                Layout.alignment:Qt.AlignLeft | Qt.AlingTop

                ButtonGroup{
                    buttons:wifiOptions.children

                }

                RadioButton{
                    id:credentialWiredOption
                    checked:getLoginOption(0)
                    visible:!enableWifiCb.checked
                    text:i18nd("lliurex-login-control","Access using user credentials")
                    onToggled:{
                        loginControlBridge.manageLoginOptions(0)
                    }
                }

                RadioButton{
                    id:credentialOption
                    checked:getLoginOption(1)
                    visible:enableWifiCb.checked
                    text:i18nd("lliurex-login-control","Access using user credentials")
                    onToggled:{
                        loginControlBridge.manageLoginOptions(1)
                        confirmPasswordValue.text=""
                    }
                }

                RadioButton{
                    id:autoLoginOption
                    checked:getLoginOption(3)
                    enabled:enableWifiCb.checked
                    text:i18nd("lliurex-login-control","Automatic login with alumnat user")
                    onToggled:{
                        loginControlBridge.manageLoginOptions(3)
                        confirmPasswordValue.text=""
                    }
                }

                RadioButton{
                    id:easyLoginOption
                    checked:getLoginOption(4)
                    visible:enableWifiCb.checked
                    text:i18nd("lliurex-login-control","Access using Easy-Login")
                    onToggled:{
                        loginControlBridge.manageLoginOptions(4)
                        confirmPasswordValue.text=""
                    }
                }

                RadioButton{
                    id:easyLoginWiredOption
                    checked:getLoginOption(5)
                    visible:!enableWifiCb.checked
                    text:i18nd("lliurex-login-control","Access using Easy-Login")
                    onToggled:{
                        loginControlBridge.manageLoginOptions(5)
                    }
                }
            }

        }

        GridLayout{
            id: passwordGrid
            columns: 2
            flow: GridLayout.LeftToRight
            Layout.leftMargin:25

            Text{
                id:passwordHead
                Layout.columnSpan:2
                text:i18nd("lliurex-login-control","Password for wifi connection with alumnat or Easy-Login:")

            }
            
            Text{
                id:password
                Layout.alignment:Qt.AlignRight
                text:i18nd("lliurex-login-control","Password:")
                font.pointSize: 10
                Layout.leftMargin:25
            }
            
            RowLayout{
                TextField{
                    id:passwordValue
                    font.pointSize:10
                    horizontalAlignment:TextInput.AlignLeft
                    focus:true
                    text:loginControlBridge.currentPassword
                    enabled:autoLoginOption.checked || easyLoginOption.checked
                    readOnly:!loginControlBridge.passwordEntryEnabled
                    implicitWidth:200
                    echoMode:TextInput.Password

                    onTextChanged:{
                        debounceTimer.callback= ()=>loginControlBridge.changeInPasswordEntry({"password":passwordValue.text,"confirmPassword":confirmPasswordValue.text})
                        debounceTimer.restart()
                    }
                }

                Button {
                    id:showPasswdBtn
                    display:AbstractButton.IconOnly
                    icon.name:getConfiguration(passwordValue.echoMode,"iconName")
                    hoverEnabled:true
                    visible:enableWifiCb.checked && (autoLoginOption.checked || easyLoginOption.checked)
                    enabled: visible && passwordValue.text!==""
                    ToolTip.delay: 1000
                    ToolTip.timeout: 3000
                    ToolTip.visible: hovered
                    ToolTip.text:getConfiguration(passwordValue.echoMode,"toolTip")
   
                    onClicked:{
                        passwordValue.echoMode=(passwordValue.echoMode===TextInput.Password)
                        ? TextInput.Normal
                        :TextInput.Password
                    }
                }

                Button {
                    id:editPasswdBtn
                    display:AbstractButton.IconOnly
                    icon.name:!loginControlBridge.passwordEntryEnabled?"document-edit":"dialog-cancel"
                    visible:loginControlBridge.showEditPasswordBtn
                    hoverEnabled:true
                    enabled: enableWifiCb.checked && (autoLoginOption.checked || easyLoginOption.checked)
                    ToolTip.delay: 1000
                    ToolTip.timeout: 3000
                    ToolTip.visible: hovered
                    ToolTip.text: !loginControlBridge.passwordEntryEnabled
                                   ?i18nd("lliurex-login-control","Click to edit password")
                                   :i18nd("lliurex-login-control","Click to cancel password editing")
                    onClicked:{
                        loginControlBridge.editPasswordBtn()
                    }
                }

                Button {
                    id:clearPasswdBtn
                    display:AbstractButton.IconOnly
                    icon.name:"edit-clear"
                    visible:loginControlBridge.showClearPasswordBtn
                    enabled:true
                    ToolTip.delay: 1000
                    ToolTip.timeout: 3000
                    ToolTip.visible: hovered
                    ToolTip.text:i18nd("lliurex-login-control","Click to clear password")
                    hoverEnabled:true
                    onClicked:{
                        clearPasswordDialog.open()
                    }
                }
            }
                
            Text{
                id:confirmPassword
                text:i18nd("lliurex-login-control","Confirm password:")
                font.pointSize: 10
                visible: loginControlBridge.showConfirmPassword
                Layout.leftMargin:25
            }
                
            RowLayout{
                id:confirmPasswordRow
                visible: loginControlBridge.showConfirmPassword
                
                TextField{
                    id:confirmPasswordValue

                    font.pointSize:10
                    horizontalAlignment:TextInput.AlignLeft
                    focus:true
                    implicitWidth:200
                    echoMode:TextInput.Password

                    onVisibleChanged:{
                        confirmPasswordValue.text=""
                    }

                    onTextChanged:{
                        
                        if (confirmPasswordValue.text===""){
                            return   
                        }

                        debounceTimer.callback= ()=>loginControlBridge.changeInConfirmPasswordEntry({"password":passwordValue.text,"confirmPassword":confirmPasswordValue.text})
                        debounceTimer.restart()
                    }
                }

                Button {
                    id:showConfirmPasswdBtn
                    display:AbstractButton.IconOnly
                    icon.name:getConfiguration(confirmPasswordValue.echoMode,"iconName")
                    ToolTip.delay: 1000
                    ToolTip.timeout: 3000
                    ToolTip.visible: hovered
                    ToolTip.text:getConfiguration(confirmPasswordValue.echoMode,"toolTip")
                    hoverEnabled:true
                    enabled:confirmPasswordValue.text!==""?true:false
                    onClicked:{
                       confirmPasswordValue.echoMode=(confirmPasswordValue.echoMode===TextInput.Password)
                          ?TextInput.Normal
                          :TextInput.Password
                    }
                }
            }
        }

        CheckBox {
                id:enableGuestCb
                text:i18nd("lliurex-login-control","Activate a guest user account (no network connection if using Wi-Fi)")
                checked:loginControlBridge.isGuestUserEnabled
                font.pointSize: 10
                focusPolicy: Qt.NoFocus
                Keys.onReturnPressed: enableGuestCb.toggled()
                Keys.onEnterPressed: enableGuestCb.toggled()
                onToggled:{
                    loginControlBridge.manageGuestUser(checked)
                }

                Layout.alignment:Qt.AlignLeft
                Layout.topMargin:20
         }

        Item { Layout.fillHeight: true }

    }

    RowLayout{
        id:btnBox
        anchors.bottom: parent.bottom
        anchors.right:parent.right
        anchors.margins:15
        spacing:10

        Button {
            id:applyBtn
            visible:true
            focus:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-ok"
            text:i18nd("lliurex-login-control","Apply")
            enabled:loginControlBridge.changesInLoginSettings 
                    ?true
                    :false
            Keys.onReturnPressed: applyBtn.clicked()
            Keys.onEnterPressed: applyBtn.clicked()
            onClicked:{
                closeTimer.stop()
                loginControlBridge.applyChanges()
                
            }
        }

        Button {
            id:cancelBtn
            visible:true
            focus:true
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-cancel"
            text:i18nd("lliurex-login-control","Cancel")
            enabled:loginControlBridge.changesInLoginSettings
            Keys.onReturnPressed: cancelBtn.clicked()
            Keys.onEnterPressed: cancelBtn.clicked()
            onClicked:{
                closeTimer.stop()
                loginControlBridge.cancelChanges()
            }
        }
    } 

    ChangesDialog{
        id:wifiChangesDialog
        dialogVisible:loginControlBridge.showChangesDialog
        dialogMsg:i18nd("lliurex-login-control","The are pending changes to apply.\nDo you want apply the changes or discard them?")
        btnAcceptVisible:true
        btnDiscardText:i18nd("lliurex-login-control","Discard")
        btnDiscardVisible:true
        btnDiscardIcon:"delete"
        btnCancelText:i18nd("lliurex-login-control","Cancel")
        btnCancelIcon:"dialog-cancel"
        Connections{
            target:wifiChangesDialog
            function onDialogApplyClicked(){
                loginControlBridge.manageChangesDialog("Accept")
            }
            function onDiscardDialogClicked(){
                loginControlBridge.manageChangesDialog("Discard")
            }
            function onRejectDialogClicked(){
                closeTimer.stop()
                loginControlBridge.manageChangesDialog("Cancel")
            }

        }
    }

    ChangesDialog{
        id:clearPasswordDialog
        dialogVisible:false
        dialogMsg:i18nd("lliurex-login-control","Do you want to delete the password for alumnat user?")
        btnAcceptVisible:false
        btnDiscardVisible:true
        btnDiscardText:i18nd("lliurex-login-control","Accept")
        btnDiscardIcon:"dialog-ok"
        btnCancelText:i18nd("lliurex-login-control","Cancel")
        btnCancelIcon:"dialog-cancel"
        Connections{
            target:clearPasswordDialog
            function onDiscardDialogClicked(){
                clearPasswordDialog.close()
                loginControlBridge.clearPassword()
            }
            function onRejectDialogClicked(){
                clearPasswordDialog.close()
            }

        }
    }
    ChangesDialog{
        id:cdcWarning
        dialogVisible:loginControlBridge.showCDCWarning
        dialogMsg:i18nd("lliurex-login-control","It is necessary to activate the integration with Digital Identitiy to be able to log in with WIFI GVA")
        btnAcceptVisible:false
        btnDiscardVisible:false
        btnCancelText:i18nd("lliurex-login-control","Close")
        btnCancelIcon:"dialog-close"
        Connections{
            target:cdcWarning
            function onRejectDialogClicked(){
                loginControlBridge.manageCDCWarning()
            }

        }
    }

    CustomPopup{
        id:synchronizePopup
    }

    function getMessageText(code){

        switch (code){
            case 10:
                return i18nd("lliurex-login-control","Changes applied successfully");
            case 20:
                return i18nd("lliurex-login-control","It is necessary to activate the integration with Digital Identity to be able to log in with WIFI GVA")
            case 30:
                return i18nd("lliurex-login-control","The default login option is configured to use Easy-Login but its activation has failed")
            case 40:
                return i18nd("lliurex-login-control","The default login option is configured to use Auto-Login but its activation has failed")
            case -10:
                return i18nd("lliurex-login-control","Error reloading configuration")
            case -20:
                return i18nd("lliurex-login-control","Error changing login settings")
            case -30:
                return i18nd("lliurex-login-control","Error 
                activating Auto-Login")
            case -40:
                return i18nd("lliurex-login-control","The Auto-Login setting could not be disabled")
            case -50:
                return i18nd("lliurex-login-control","Error activating Easy-Login")
            case -60:
                return i18nd("lliurex-login-control","The Easy-Login setting could not be disabled")
            case -70:
                return i18nd("lliurex-login-control","Error changing guest user activation")
            case -80:
                return i18nd("lliurex-login-control","Multiple errors have ocurred while applying changes")
            case -90:
                return i18nd("lliurex-login-control","Passwords must match")
            case -100:
                return i18nd("lliurex-login-control","You must enter a password")
            case -110:
                return i18nd("lliurex-login-control","Error changing password for Auto-Login or Easy-Login")
            default:
                return ""
        }

    }

    function getTypeMessage(msgType) {
        switch (msgType) {
            case 0:
                return Kirigami.MessageType.Positive
            case 1:
                return Kirigami.MessageType.Error
            case 2:
                return Kirigami.MessageType.Warning
            case 3:
                return Kirigami.MessageType.Information
           default:
                return Kirigami.MessageType.Information
        }
    }

    function getLoginOption(option){

        const currentOption=loginControlBridge.currentLoginOption

        if (currentOption === 0){
            return option === 0
        }

        if (currentOption === 1 || currentOption === 2){
            return option === 1
        }

        if (currentOption === 3){
            return option === 3
        }

        if (currentOption === 4){
            return option === 4
        }

        if (currentOption === 5){
            return option === 5
        }

        return false
       
    }

    function getConfiguration(echoMode,type){

        const isPasswordHidden= (echoMode===TextInput.Password)

        if (type=="toolTip"){
            return isPasswordHidden
                ? i18nd("lliurex-login-control","Click to show password")
                : i18nd("lliurex-login-control","Click to hide password")
        }

        return isPasswordHidden?"visibility":"view-hidden"
        
    }

} 
