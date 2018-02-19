var diagram = null;

function generateGraph(nodes) {
    var $$ = go.GraphObject.make;
    if (diagram !== null) {
        diagram.div = null;
    }
    diagram = $$(go.Diagram, "intent-graph",
        {
            initialContentAlignment: go.Spot.Center, // center Diagram contents
            "undoManager.isEnabled": true, // enable Ctrl-Z to undo and Ctrl-Y to redo
            initialDocumentSpot: go.Spot.TopCenter,
            initialViewportSpot: go.Spot.TopCenter
        });

    //Define the node templates
    diagram.nodeTemplate =
        $$(go.Node, "Auto",
            // The outer shape of the node surrounding the table
            $$(go.Shape, "Rectangle",
                { stroke: null, strokeWidth: 0 },
                {margin: -12},
                /* reddish if highlighted, blue otherwise */
                new go.Binding("fill", "isHighlighted", function(h) { return h ? "#F44336" : "#2196f3"; }).ofObject()
            ),

            // A table to contain different parts of the node
            $$(go.Panel, "Table",
                {margin: 6},
                //Name of node
                $$(go.TextBlock,
                    {
                        row: 0, column: 0,
                        maxSize: new go.Size(160, NaN), margin: 2,
                        font: "500 16px Roboto, sans-serif",
                        stroke: "white",
                        alignment: go.Spot.Top
                    },
                    new go.Binding("text", "name")
                ),
                //Priority
                $$(go.TextBlock,
                    {
                        row: 1, column: 0,
                        font: "12px Roboto, sans-serif"
                    },
                    new go.Binding("text", "priority")
                ),
                //Preconditions
                $$(go.TextBlock,
                    {
                        row: 2, column: 0,
                        font: "12px Roboto, sans-serif"
                    },
                    new go.Binding("text", "preconditions")
                )
            )
        );

    var nodeDataArray = [];
    var linkDataArray = [];

    if (nodes !== null) {
        for (var i = 0; i < nodes.length; i++) {
            var node = nodes[i];
            var nodeData = {};
            nodeData["key"] = i;
            nodeData["name"] = node.name;
            nodeData["priority"] = "Priority: " + node.priority;
            nodeData["preconditions"] = "Preconditions:\n" + node.preconditions;
            nodeDataArray.push(nodeData);
        }

        for (i = 0; i < nodes.length; i++) {
            for (var j = 0; j < nodes.length; j++) {
                if (j !== i) {
                    var link = {};
                    link['from'] = i;
                    link['to'] = j;
                    linkDataArray.push(link);
                }
            }
        }
    }

    var model = $$(go.GraphLinksModel);
    model.nodeDataArray = nodeDataArray;
    model.linkDataArray = linkDataArray;
    diagram.model = model;
}