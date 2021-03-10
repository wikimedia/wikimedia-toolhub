<template>
	<div v-frag>
		<v-text-field
			v-if="widget === 'text'"
			v-model="model"
			:label="ui.label"
			:required="ui.required"
			:rules="validationRules"
			:prepend-icon="ui.icon"
			:hint="schema.description"
			:counter="schema.maxLength"
			clearable
		/>
		<v-textarea
			v-else-if="widget === 'multiline'"
			v-model="model"
			:label="ui.label"
			:required="ui.required"
			:rules="validationRules"
			:prepend-icon="ui.icon"
			:hint="schema.description"
			:counter="schema.maxLength"
			rows="1"
			auto-grow
			clearable
		/>
		<v-autocomplete
			v-else-if="widget === 'select'"
			v-model="model"
			:label="ui.label"
			:rules="validationRules"
			:prepend-icon="ui.icon"
			:hint="schema.description"
			:items="ui.select.items()"
			:multiple="ui.multiple || false"
			:deletable-chips="ui.multiple || false"
			:small-chips="ui.multiple || false"
			:clearable="ui.multiple ? false : true"
		/>
		<v-combobox
			v-else-if="widget === 'multi-select'"
			v-model="model"
			:label="ui.label"
			:rules="validationRules"
			:prepend-icon="ui.icon"
			:hint="schema.description"
			multiple
			deletable-chips
			small-chips
		/>
		<v-checkbox
			v-else-if="widget === 'checkbox'"
			v-model="model"
			:label="ui.label"
		/>
		<template v-else-if="widget === 'array'">
			<v-row
				v-for="( obj, idx ) in value"
				:key="idx"
			>
				<v-col sm="11"
					cols="10"
				>
					<InputWidget
						v-model="model[ idx ]"
						:schema="schema.items"
						:ui-schema="ui.items"
					/>
				</v-col>

				<template
					v-if="ui.items.widget === 'url-multilingual'"
				>
					<v-col v-if="idx === 0"
						sm="1"
						cols="2"
					>
						<v-btn
							elevation="2"
							icon
							class="mt-2"
							color="primary"
							@click="alterArray( 'add', value )"
						>
							<v-icon>
								mdi-plus
							</v-icon>
						</v-btn>
					</v-col>

					<v-col v-else
						sm="1"
						cols="2"
					>
						<v-btn
							elevation="2"
							icon
							class="mt-2"
							color="error"
							@click="alterArray( 'remove', value, idx )"
						>
							<v-icon>
								mdi-minus
							</v-icon>
						</v-btn>
					</v-col>
				</template>
			</v-row>
		</template>
		<template v-else-if="widget === 'url-multilingual'">
			<v-col cols="12">
				<InputWidget
					v-model="model.url"
					:schema="schema.properties.url"
					:ui-schema="ui.url"
				/>
			</v-col>
			<v-col cols="12">
				<InputWidget
					v-model="model.language"
					:schema="schema.properties.language"
					:ui-schema="ui.language"
				/>
			</v-col>
		</template>
		<pre v-else>
			{{ schema }}
		</pre>
	</div>
</template>

<script>
import urlRegex from '@/plugins/url-regex';
import patternRegexRule from '@/plugins/pattern-regex';

export const methods = {
	/**
	 * Initialize our model based on our value and schema.
	 */
	initModel() {
		if ( this.value ) {
			if (
				this.schema.type === 'object' &&
				Object.keys( this.value ).length > 0
			) {
				this.model = this.value;
			} else if (
				this.schema.type === 'array' &&
				this.value.length > 0
			) {
				this.model = this.value;
			} else if (
				this.schema.type === 'boolean' &&
				this.value !== null
			) {
				this.model = this.value;
			} else if (
				this.schema.type === 'string' ||
				this.schema.type === 'number' ||
				this.schema.type === 'integer'
			) {
				this.model = this.value;
			} else {
				this.model = this.initBlankValue();
			}
		} else {
			this.model = this.initBlankValue();
		}
	},

	initBlankValue() {
		switch ( this.schema.type ) {
			case 'object':
				return {};
			case 'array':
				return [];
			case 'boolean':
				return false;
			case 'number':
			case 'integer':
				return null;
			default:
				return '';
		}
	},

	/**
	 * Grow/shrink an array type.
	 *
	 * @param {string} op - operation to perform ('add' or 'remove')
	 * @param {Array} data - Array to modify
	 * @param {number?} index - Index of item to remove
	 */
	alterArray( op, data, index ) {
		if ( op === 'remove' ) {
			if ( data.length > 1 ) {
				data.splice( index, 1 );
			}
		} else if ( op === 'add' ) {
			// TODO: make this configurable
			data.push( { url: '', language: 'en' } );
		}
	}
};

export default {
	name: 'InputWidget',
	props: {
		schema: {
			type: Object,
			default: () => {},
			required: true
		},
		uiSchema: {
			type: Object,
			default: () => {}
		},
		value: {
			type: [ String, Number, Boolean, Array, Object ],
			default: ''
		}
	},
	data: () => ( {
		model: null
	} ),
	computed: {
		/**
		 * Get our UI helper data.
		 *
		 * @return {Object}
		 */
		ui() {
			return this.schema[ 'x-ui' ] || this.uiSchema;
		},
		widget() {
			if ( this.ui.widget ) {
				return this.ui.widget;
			}
			if ( this.schema.type === 'string' ) {
				if ( this.schema.enum ) {
					return 'select';
				}
				return this.schema.maxLength > 2047 ? 'multiline' : 'text';
			}
			return this.schema.type;
		},
		validationRules() {
			const schema = this.schema;
			const ui = this.ui;
			const rules = [];
			if ( schema.maxLength ) {
				rules.push(
					( v ) => ( v || '' ).length <= schema.maxLength ||
						this.$t( 'charslimit', [ schema.maxLength ] )
				);
			}
			if ( schema.pattern ) {
				rules.push( ...patternRegexRule( schema.pattern ) );
			}
			if ( schema.format === 'uri' ) {
				rules.push(
					( v ) => !v ? true : urlRegex.test( v ) ||
					this.$t( 'urlinvalid' )
				);
			}
			if ( ui.required === true ) {
				rules.push( ( v ) => !!v || this.$t( 'required-field' ) );
			}
			return rules;
		}
	},
	methods,
	watch: {
		model: {
			handler( newVal ) {
				this.$emit( 'input', newVal );
			},
			deep: true,
			immediate: true
		},
		value: {
			handler( newVal, oldVal ) {
				if ( JSON.stringify( oldVal ) !== JSON.stringify( newVal ) ) {
					this.initModel();
				}
			},
			deep: true
		}
	},
	created() {
		this.initModel();
	}
};
</script>
