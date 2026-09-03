import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: mainGrid
    spacing: 10

    Rectangle {
        id: sideBar
        width: 160
        Layout.fillHeight: true
        border.color: palette.mid

        ColumnLayout {
            id: menuLayout
            Layout.fillWidth:true
            Layout.fillHeight: true
            spacing: 0

            MenuOptionBtn {
                id: listItem
                Layout.fillWidth: true
                optionText:i18nd("lliurex-login-control","Configuration")
                optionIcon: "configure"
                onMenuOptionClicked: loginControlBridge.manageTransitions(0)
            }

            MenuOptionBtn {
                id: helpItem
                Layout.fillWidth: true
                optionText: i18nd("lliurex-login-control", "Help")
                optionIcon: "help-contents"
                onMenuOptionClicked: loginControlBridge.openHelp()
            }

            Item {
                    Layout.fillHeight:true

            }
        }
    }

    StackView {
        id: optionsView
        Layout.fillWidth: true
        Layout.fillHeight: true

        property int currentIndex: loginControlBridge.currentOptionsStack
        initialItem:loginView

        onCurrentIndexChanged: {
            switch(currentIndex){
                case 0:
                    optionsView.replace(loginView)
                    break;
            }
        }

        replaceEnter: Transition {
            NumberAnimation {
                property: "opacity"
                from: 0
                to: 1
                duration: 60
            }
        }
        replaceExit: Transition {
            NumberAnimation {
                property: "opacity"
                from: 1
                to: 0
                duration: 60
            }
        }

        Component{
            id:loginView
            LoginOptions{
                id:loginOptions
            }
        }
    }
}
