<template>
	<v-tooltip top>
		<template #activator="{ on, attrs }">
			<v-btn
				v-show="show"
				v-scroll="onScroll"
				fab
				dark
				fixed
				bottom
				right
				color="primary"
				v-bind="attrs"
				@click="scrollToTop"
				v-on="on"
			>
				<v-icon>mdi-chevron-up</v-icon>
			</v-btn>
		</template>
		<span>{{ $t( 'scrolltotop' ) }}</span>
	</v-tooltip>
</template>

<script>
export default {
	name: 'ScrollTop',
	data() {
		return {
			show: false
		};
	},
	methods: {
		onScroll( e ) {
			if ( typeof window === 'undefined' ) {
				return;
			}
			const top = window.pageYOffset || e.target.scrollTop || 0;
			this.show = top > 20;
		},
		scrollToTop() {
			this.$vuetify.goTo( 0 );
		}
	}
};
</script>
