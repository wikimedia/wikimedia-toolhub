<template>
	<v-container id="notifications">
		<v-row>
			<v-col cols="12">
				<v-alert
					v-for="message in messages"
					:key="message.id"
					:type="message.type"
					:prominent="message.prominent"
					:dense="message.prominent"
					border="left"
					class="mx-auto"
					dismissible
					transition="fade-transition"
					:close-label="$t( 'message-close' )"
					@input="close( message )"
				>
					{{ message.message }}
				</v-alert>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapState, mapMutations } from 'vuex';

export default {
	computed: {
		...mapState( 'notify', [ 'messages' ] )
	},

	methods: {
		...mapMutations( 'notify', [ 'onClearMessage' ] ),

		/**
		 * Remove a message.
		 *
		 * @param {Object} payload - Message object
		 * @param {string} payload.id = Message id
		 */
		close( payload ) {
			this.onClearMessage( payload.id );
		}
	}
};
</script>
