<template>
	<v-menu
		ref="menu"
		v-model="menu"
		:close-on-content-click="false"
		transition="scale-transition"
		offset-y
		min-width="auto"
		left
	>
		<template #activator="{ on, attrs }">
			<v-text-field
				:value="formattedDate"
				:label="label"
				prepend-icon="mdi-calendar"
				readonly
				v-bind="attrs"
				v-on="on"
			/>
		</template>
		<v-date-picker
			:value="date"
			no-title
			scrollable
			color="primary"
			:locale="locale"
			:first-day-of-week="firstDayOfWeek"
			@input="emit"
		/>
	</v-menu>
</template>

<script>
import { mapState } from 'vuex';

export default {
	name: 'DatePicker',
	props: {
		/**
		 * Initial value in YYYY-MM-DD(THH:mm:SS) format.
		 */
		value: {
			type: String,
			default: null,
			required: false
		},
		/**
		 * Moment format string for display of selected date.
		 */
		displayFormat: {
			type: String,
			default: 'll',
			required: false
		},
		/**
		 * Input label.
		 */
		label: {
			type: String,
			default: null,
			required: false
		},
		/**
		 * Output suffix, often a time string like 'T00:00Z'.
		 */
		suffix: {
			type: String,
			default: '',
			required: false
		}
	},
	data: () => ( {
		menu: false
	} ),
	computed: {
		...mapState( 'locale', [ 'locale' ] ),
		date() {
			return this.value ? this.value.substring( 0, 10 ) : this.value;
		},
		firstDayOfWeek() {
			return this.$moment.localeData( this.locale ).firstDayOfWeek();
		},
		formattedDate() {
			return this.date ?
				this.$moment.utc( this.date ).format( this.displayFormat ) :
				'';
		}
	},
	methods: {
		emit( data ) {
			const date = data ? data + this.suffix : data;
			this.$emit( 'input', date );
			this.menu = false;
		}
	}
};
</script>
