import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

var Circle = React.createClass({
    render: function() {
        return (
            <View style={styles.circle} />
        )
    }
});


circle: {
    width: 100,
    height: 100,
    borderRadius: 100/2,
    backgroundColor: 'red'
}

