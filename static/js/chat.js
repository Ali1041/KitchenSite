
// import ChatEnable from './index'

	  $(function () {

			const value = JSON.parse(document.getElementById('username').textContent);
			console.log(value)
			const roomName = JSON.parse(document.getElementById('room').textContent)
            console.log(roomName,value)
			// console.log(ChatEnable)
            let completeMsgList = []
            let $topWindow = $("#top")
            // Reference to the chat messages area
            let $chatWindow = $("#messages");
            let $chatNewWindow = $("#messages1")
            // Our interface to the Chat service
            let chatClient;

            // A handle to the room's chat channel
            let roomChannel;

            // The server will assign the client a random username - stored here
            let username;


            // Enabling typing
            function enableTyping() {
                const input = $("#message-input")
                input.removeAttr('disabled')
                input[0].innerHTML = ''
            }

            // Helper function to print info messages to the chat window
            function print(infoMessage, asHtml) {
                let $msg = $('<div class="info text-center">');
                if (asHtml) {
                    $msg.html(infoMessage);
                } else {
                    $msg.text(infoMessage);
                }
                $topWindow.append($msg);
            }

            // Helper function to print chat message to the chat window
            function printMessage(fromUser, message, time) {
                let $user = $('<small class="username" style="font-weight: 700;color: rgb(46, 154, 135)">').text(fromUser + ": ");
                if (fromUser === username) {
                    $user.addClass("me");
                }
                let $msgDiv = $('<div class=" message p-2 my-2 bg-light">')
                let $message = $('<p class="m-0">').text(message);
                let $container = $('<div class="message-container" style="margin: 5px 0">');

                let $date = $(`<p class="m-0 date align-self-end mt-1 w-100 text-right" style="font-size: 11px">`).html(`${time}`)
                $msgDiv.append($user).append($message)
                $msgDiv.append($date)
                $container.append($user)
                $container.append($msgDiv)

                $chatWindow.append($container);
                if ($chatNewWindow[0] === undefined) {

                } else {
                    $chatNewWindow.scrollTop($chatNewWindow[0].scrollHeight);
                }
            }

            // Get an access token for the current user, passing a device ID
            // for browser-based apps, we'll just use the value "browser"
            $.getJSON(
                "/token",
                {
                    device: "browser"
                },
                function (data) {
                    // Alert the user they have been assigned a random username
                    username = data.identity;
                    print(
                        "Your username for this chat is: " +
                        '<span class="me">' +
                        username +
                        "</span>",
                        true
                    );

                    // Initialize the Chat client
                    // chatClient = new Twilio.Chat.Client(data.token);

                    Twilio.Chat.Client.create(data.token).then(client => {
                        // Use client
                        chatClient = client;
                        chatClient.getSubscribedChannels().then(createOrJoinChannel);
                    });
                }
            );

            // Set up channel after it has been found / created
            function setupChannel(name) {
                roomChannel.join().then(function (channel) {
                    print(
                        `Joined channel ${name} as <span class="me"> ${username} </span>.`,
                        true
                    );
                    channel.getMessages(30).then(processPage);
                })
                    .catch(() => {

                        roomChannel.getMessagesCount()
                            .then((res) => {
                                if (res < 99) {
                                    roomChannel.getMessages(res).then(processPage)
                                } else {
                                    roomChannel.getMessages(99).then(processPage)
                                }
                            })
                    })

                // Listen for new messages sent to the channel
                roomChannel.on("messageAdded", function (message) {
                    printMessage(message.author, message.body, message.dateUpdated);
                    if (message.author !== value) {

                        fetch(`${location.origin}/send_push/`, {
                            method: 'POST',
                            body: JSON.stringify({
                                author: message.author,
                                body: message.body
                            })
                        })
                            .then((res) => {
                                return res.json()
                            })
                            .then((result) => {
                                console.log(result)
                            })
                            .catch((err) => {
                                console.log(err)
                            })
                    }
                });
            }

            function processPage(page) {
                if (page.items.length === 99) {
                    page.items.forEach(message => {

                        printMessage(
                            message.author,
                            message.body,
                            message.timestamp
                        )

                    });
                } else {
                    page.items.forEach(message => {

                        completeMsgList.push({
                            author: message.author,
                            body: message.body,
                            time: message.timestamp
                        })

                    });

                    if (page.hasPrevPage) {
                        page.prevPage().then(processPage);
                    } else {
                        console.log("Done loading messages");
                        completeMsgList.forEach((item) => {
                            printMessage(item.author, item.body, item.time);
                        })
                    }
                }
            }

            function createOrJoinChannel(channels) {
                // Extract the room's channel name from the page URL
	            let channelName = roomName
                if (channelName===''){
                    channelName = value
                }
                print(`Connected you to "${channelName}" chat channel...`);

                chatClient
                    .getChannelByUniqueName(channelName)
                    .then(function (channel) {
                        roomChannel = channel;
                        console.log("Found channel:", channelName);
                        setupChannel(channelName);
                        enableTyping()
                    })
                    .catch(function () {
                        // If it doesn't exist, let's create it
                        chatClient
                            .createChannel({
                                uniqueName: channelName,
                                friendlyName: `${channelName} Chat Channel`
                            })
                            .then(function (channel) {
                                roomChannel = channel;
                                setupChannel(channelName);
                                enableTyping()
                            });
                    });
            }

            // Add newly sent messages to the channel
            let $form = $("#message-form");
            let $input = $("#message-input");
            $form.on("submit", function (e) {
                e.preventDefault();
                if (roomChannel && $input.val().trim().length > 0) {
                    roomChannel.sendMessage($input.val());
                    $input.val("");
                }
            });
        });
