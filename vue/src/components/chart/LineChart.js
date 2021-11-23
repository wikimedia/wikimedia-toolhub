// Component for line charts.
// The chart updates when the data changes.
import {
	Line,
	mixins
} from 'vue-chartjs';

export default {
	name: 'LineChart',
	extends: Line,
	mixins: [ mixins.reactiveProp ],
	data() {
		return {
			options: {
				scales: {
					yAxes: [ {
						ticks: {
							beginAtZero: true
						},
						gridLines: {
							display: true
						}
					} ],
					xAxes: [ {
						gridLines: {
							display: false
						}
					} ]
				},
				legend: {
					display: true
				},
				responsive: true,
				maintainAspectRatio: false
			}
		};
	},
	mounted() {
		// this.chartData is a property declared by the reactiveProp mixin.
		this.renderChart( this.chartData, this.options );
	}
};
