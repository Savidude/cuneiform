OrderIntent {
	var address;

	node getOrderType {
		priority : 7;

		preconditions {
			Slot.type == null
		}

		action {
			var response = new Response;
            response.responseSet = [
                "Would you like delivery or takeaway?",
                "Would you like takeaway or delivery?",
                "Would you like your pizza delivered or is it takeaway?"
            ];
            response.userAction = "answer";
            response.send;

            var type = Slot.type;
          	while (type == null) {
            	response.send;
              	type = Slot.type;
            }
		
		    Initiate;
		}
	}
	node getTime {
		priority : 6;

		preconditions {
			Slot.time == null && Slot.type != null
		}

		action {
			var orderType = Slot.type;
          	var response = new Response;
          	var responses;
          
          	if (orderType == "delivery") {
              	responses = [
                	"When would you like it delivered?",
                  	"At what time would you like your delivery?"
                ];
            } elif (orderType == "takeaway") {
            	responses = [
                	"When would you like to pick up your order?",
                  	"At what time would you like to pick up your order?"
                ];
            }
          
          	response.responseSet = responses;
          	response.userAction = "answer";
          	response.send;
          
            var time = Slot.time;
            while (time == null) {
              	response.send;
              	time = Slot.time;
            }

            Initiate;
		}
	}
	node getAddress {
		priority : 5;

		preconditions {
			address == null && Slot.type == "delivery"
		
		}

		action {
			var response = new Response;
          	response.responseSet = [
            	"What is your address?",
              	"Which address would you like your pizza delivered to?",
              	"Could you please tell me your address?",
              	"May I know your address?"
            ];
          	response.userAction = "command";
          	address = response.send;
          
          	Initiate;
		}
	}
	node searchPizza {
		priority : 4;

		preconditions {
			Slot.type != null && Slot.time != null
		}

		action {
			var typeResponse = new Response;
            typeResponse.responseSet = [
                "What choice of pizza would you like to get?",
                "What type of pizza would you like?",
                "What kind of pizza do you want to order?"
            ];
            typeResponse.userAction = "command";
            var typeName = typeResponse.send;

            var http = new HTTP;
            http.method = "post";
            http.url = "https://pizzashop-sample.herokuapp.com/api/pizza/search";
            http.data = {name : typeName};

            var r = http.request;
          	var crusts = r["crusts"];

            var crustsMsg = "What kind of crust would you prefer? We have";
          	for crust in crusts {
          	    var crustName = crust["name"];
          	    crustsMsg = crustsMsg + " " + crustName + ",";
          	}
          	var crustResponse = new Response;
          	crustResponse.responseSet = [crustsMsg];
          	crustResponse.userAction = "select";
          	crustResponse.options = {
          	    Pan : [
          	        "I would like a pan crust",
          	        "Pan crust please",
          	        "Pan crust",
          	        "Pan"
          	    ],
          	    Stuffed : [
          	        "I would like a stuffed crust",
          	        "Stuffed crust please",
          	        "Stuffed crust",
          	        "Stuffed"
          	    ],
          	    Sausage  : [
          	        "I would like a sausage crust",
          	        "Sausage crust please",
          	        "Sausage crust",
          	        "Sausage"
          	    ]
          	};
          	var selectedCrust = crustResponse.send;

          	var sizesMsg = "Which size do you want to order? For " + selectedCrust + " we have";
          	for crust in crusts {
          	    crustName = crust["name"];
          	    if (selectedCrust == crustName) {
          	        var sizes = crust["sizes"];
          	        for size in sizes {
          	            sizesMsg = sizesMsg + " " + size + ", ";
          	        }
          	    }
          	}
          	var sizeResponse = new Response;
          	sizeResponse.responseSet = [sizesMsg];
          	sizeResponse.userAction = "select";
          	sizeResponse.options = {
          	    Personal : [
          	        "I would like a personal pizza",
          	        "Give me a personal pizza",
          	        "Personal please",
          	        "Personal"
          	    ],
                Medium : [
          	        "I would like a medium pizza",
          	        "Give me a medium pizza",
          	        "Medium please",
          	        "Medium"
          	    ],
          	    Large : [
          	        "I would like a large pizza",
          	        "Give me a large pizza",
          	        "Large please",
          	        "Large"
          	    ]
          	};
          	var selectedSize = sizeResponse.send;

          	var summaryResponse = new Response;
          	var summary = "You have ordered a " + typeName + " pizza with " + selectedCrust + " crust of size " + selectedSize + ". Is this correct?";
          	summaryResponse.responseSet = [summary];
          	summaryResponse.userAction = "confirm";
          	var confirmation = summaryResponse.send;

          	if (confirmation == 1) {
          	    var  confirmationResponse = new Response;
          	    confirmationResponse.responseSet = [
          	        "Your order has been placed. Thank you for choosing to dine with us.",
          	        "Your order has been placed."
          	    ];
          	    confirmationResponse.userAction = "info";
          	    confirmationResponse.send;
              
              var time = Slot.time;
              var dateTime = time.toString;

              var orderData = {
                  name : typeName,
                  crust : selectedCrust,
                  size : selectedSize,
                  address : address,
                  time : dateTime
              };
              var http = new HTTP;
              http.method = "post";
              http.url = "https://pizzashop-sample.herokuapp.com/api/order/add";
              http.data = orderData;
              var r = http.request;

          	} else {
          	    var  confirmationResponse = new Response;
          	    confirmationResponse.responseSet = [
          	        "K. Bye."
          	    ];
          	    confirmationResponse.userAction = "info";
          	    confirmationResponse.send;
          	}

          	ExitIntent;
		}
	}
}