<template>
	<v-container>
		<v-dialog
			v-model="show"
			persistent
			max-width="600px"
			@keydown.esc="show = false"
		>
			<v-card>
				<v-card-title>
					<span class="text-h5">{{ $t( 'editsummary' ) }}</span>
				</v-card-title>

				<v-card-text>
					<v-container>
						<v-row>
							<v-text-field
								ref="comment"
								v-model="comment"
								:label="$t( 'describechanges' )"
								required
								:rules="requiredRule"
								autofocus
								@keydown.enter="saveComment"
							/>
						</v-row>
					</v-container>
				</v-card-text>

				<v-card-actions>
					<v-spacer />

					<v-btn
						color="accent text--secondary"
						@click="show = false"
					>
						<v-icon
							dark
							class="me-2"
						>
							mdi-cancel
						</v-icon>
						{{ $t( 'cancel' ) }}
					</v-btn>

					<v-btn
						color="primary"
						dark
						@click="saveComment"
					>
						<v-icon
							dark
							class="me-2"
						>
							mdi-content-save-edit
						</v-icon>
						{{ $t( 'publishchanges' ) }}
					</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</v-container>
</template>

<script>
export default {
	name: 'CommentDialog',
	props: {
		value: {
			type: Boolean,
			required: false
		}
	},
	data() {
		return {
			comment: null,
			requiredRule: [ ( v ) => !!v || this.$t( 'required-field' ) ]
		};
	},
	computed: {
		show: {
			get() {
				return this.value;
			},
			set( value ) {
				this.$emit( 'input', value );
			}
		}
	},
	methods: {
		saveComment() {
			if ( !this.comment ) {
				this.$refs.comment.validate( true );
				return;
			}

			this.$emit( 'save', this.comment );
		}
	}
};
</script>
