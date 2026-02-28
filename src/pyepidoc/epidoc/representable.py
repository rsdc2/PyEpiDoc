from __future__ import annotations
import re
from functools import cached_property, reduce
from typing import Sequence

from pyepidoc.xml.xml_text import XmlText
from pyepidoc.xml.xml_element import (
    XmlComment, 
    XmlNode, 
    ProcessingInstruction
)
from pyepidoc.xml.namespace import Namespace as ns
from pyepidoc.shared.enums import (
    whitespace
)
from pyepidoc.shared.namespaces import XMLNS, TEINS
from pyepidoc.shared.enums import RegTextType
from pyepidoc.shared.classes import Showable
from pyepidoc.tei.tei_element import TeiElement
from pyepidoc.xml.xml_element import XmlElement
from pyepidoc.shared.iterables import last
from pyepidoc.shared.enums import AtomicTokenType


class RepresentableElement(TeiElement, Showable):
    """
    Represents any element that has a representation in a printed version of the
    document.
    """

    @property
    def abbr_elems(self) -> Sequence[RepresentableElement]:
        """
        Returns all abbreviation elements as a |list| of |Element|.
        """

        return [RepresentableElement(abbr) 
                for abbr in self.get_desc('abbr')]
        
    @property
    def am_elems(self) -> Sequence[RepresentableElement]:
        """
        Returns a |list| of abbreviation marker elements <am>.
        See https://tei-c.org/release/doc/tei-p5-doc/en/html/ref-am.html,
        last accessed 2023-04-13.
        """

        return [RepresentableElement(abbr) 
                for abbr in self.get_desc('am')]
    
    @property
    def expan_elems(self) -> Sequence[RepresentableElement]:
        """
        Returns all abbreviation expansions (i.e. abbreviation + expansion) 
        as a |list| of |Element|.
        """

        return [RepresentableElement(expan) 
                for expan in self.get_desc('expan')]

    def deepcopy(self) -> RepresentableElement:
        return RepresentableElement(self._e.deepcopy())

    @property
    def elem_classes(self) -> dict[str, type[RepresentableElement]]:
        from .representable_classes import representable_classes
        return representable_classes

    @property
    def is_no_break(self) -> bool:
        """
        Returns true if element is a linebreak with no word break
        """
        if self._e._e.tag == ns.give_ns('lb', TEINS):
            if self._e.attrs.get('break') == 'no':
                return True
        # TODO: Check this works
        if self._e.tag.name == 'Comment':
            return True

        return False
    
    def find_next_no_spaces(self) -> list[RepresentableElement]:

        """
        Returns a list of the next |Element|s not separated by whitespace.
        """
                
        def _find_next_no_spaces(
                acc: list[RepresentableElement], 
                element: RepresentableElement) -> list[RepresentableElement]:

            if not isinstance(element, RepresentableElement): 
                return acc

            next_sibling = element.find_next_sibling()

            if next_sibling is None:
                return acc + [element]
            
            if RepresentableElement(next_sibling).is_no_break:
                return _find_next_no_spaces(acc + [element], RepresentableElement(next_sibling))

            if element.has_whitepace_tail:
                return acc + [element]
            
            return _find_next_no_spaces(acc + [element], RepresentableElement(next_sibling))

        result = _find_next_no_spaces([], self)
        return result

    @property
    def following_nodes_in_ab(self) -> list[XmlNode]:

        """
        Returns any following Element or Text nodes whose
        ancestor is an `<ab>`.
        """

        return self._e.xpath(
            'following::node()[ancestor::x:ab]', 
            namespaces={'x': TEINS}
        )

    @cached_property
    def form(self) -> str:
        """
        Returns the full form, including any abbreviation expansion.
        Compare @normalized_form
        """

        return self._e._clean_text(self._e.text_desc)

    @property
    def form_normalized(self) -> str:
        """
        Returns the normalized form of the token, i.e.
        taking the text from <reg> not <orig>, <corr> not <sic>;
        also excludes text from <g>, <surplus> and <del> elements
        """
        return self.normalized_form
    
    def get_supplied(self) -> list[RepresentableElement]:
        return [RepresentableElement(supplied) for supplied in self.get_desc('supplied')]

    @property
    def has_lb_in_preceding_or_ancestor(self) -> XmlElement | None:

        """
        Returns any preceding or |_Element| containing an
        <lb> element.
        cf. https://www.w3.org/TR/1999/REC-xpath-19991116/#axes
        last accessed 2023-04-20.
        """

        def get_preceding_lb(elem: XmlElement) -> list[XmlElement]:
            
            result = elem.xpath('preceding::*[descendant-or-self::ns:lb]')

            if result == []:
                if elem.parent is None:
                    return []

                return get_preceding_lb(elem.parent)

            return [item for item in result
                    if isinstance(item, XmlElement)]
        
        return last(get_preceding_lb(self._e))

    @property
    def has_whitepace_tail(self) -> bool:
        """
        Returns True if the final element of the tail is a whitespace,
        implying a word break at the end of the element.
        """

        if self._e.tail is None: 
            return False
        
        if self._e.localname == 'lb' and self.get_attr('break') == 'no':
            return False
        
        if self._e.tail == '':
            return False
        
        if self._e.tag.name == "Comment":
            return False

        return self._e.tail[-1] in whitespace

    @property
    def leiden_form(self) -> str:
        """
        Returns the form per Leiden conventions, i.e. with
        abbreviations expanded with brackets
        """
        if self.representable_cls_inst is None:
            return self._e.text_desc
        if type(self.representable_cls_inst) is type(self):
            raise TypeError(f'Class {type(self)} must implement property `leiden_form`.')
        return self.representable_cls_inst.leiden_form.strip()

    @property
    def leiden_plus_form(self) -> str:
        """
        Returns the Leiden form, with 
        interpunts indicated by middle dot;
        line breaks are indicated with vertical bar '|'
        """

        def string_rep(n: XmlNode) -> str:
            """
            Get the string representation of the node, if it is 'g', 'lb', 'gap',
            otherwise return empty string.
            """
            ln = n.localname

            if isinstance(n, (XmlText, XmlComment, ProcessingInstruction)):
                return ''

            if ln in ['g', 'lb', 'gap']:
                return self.elem_classes[ln](n).leiden_form
            
            return ''

        def get_next_non_text(
                acc: list[XmlNode],
                node: XmlNode
            ) -> list[XmlNode]:

            if acc != []:
                last = acc[-1]

                if isinstance(last, XmlText):
                    if str(last).strip() not in ['', '·']:
                        return acc 
                
                if last.localname in ['lb', 'w', 'name', 'persName', 'roleName', 'num']:
                    return acc
            
            return acc + [node]

        if type(self.representable_cls_inst) is type(self):
            raise TypeError(f'Class {type(self)} must implement property `leiden_plus_form`.')
        
        preceding = reversed(self.preceding_nodes_in_ab)
        following = self.following_nodes_in_ab

        preceding_upto_text = reduce(get_next_non_text, preceding, list[XmlNode]())
        preceding_upto_text = list(reversed(preceding_upto_text))
        following_upto_text = reduce(get_next_non_text, following, list[XmlNode]())
        
        prec_text = ''.join(map(string_rep, preceding_upto_text))
        following_text = ''.join(map(string_rep, following_upto_text))

        combined = prec_text + self.leiden_form + following_text  
        combined = re.sub(r'\s+', ' ', combined).strip()
        return combined

    @property
    def local_id(self) -> str | None:
        """
        Return `@n` id
        """
        return self.get_attr('n')
    
    @local_id.setter
    def local_id(self, value: str | None) -> None:
        if value is None:
            self._e.remove_attr('n')
        else:
            self._e.set_attr('n', value)

    @property
    def xml_id(self) -> str | None:
        """
        Returns value of the xml:id attribute in the XML file.
        """
        return self.get_attr('id', namespace=XMLNS)

    @xml_id.setter
    def xml_id(self, id_value: str | None) -> None:
        """
        Sets the value of the xml:id attribute in the XML file.
        """
        if id_value is None:
            self._e.remove_attr('id', namespace=XMLNS)
        else:
            self.set_attr('id', id_value, namespace=XMLNS)

    @property
    def preceding_nodes_in_ab(self) -> list[XmlNode]:

        """
        Returns any preceding |_Element| or 
        |_ElementUnicodeResult| whose ancestor is an edition.
        """

        return self._e.xpath(
            'preceding::node()[ancestor::x:ab]', 
            namespaces={'x': TEINS}
        )

    @cached_property
    def simple_lemmatized_edition_element(self) -> RepresentableElement:
        """
        Element for use in simple-lemmatized edition
        """
        t = type(self)
        elem = t(self.deepcopy()._e)
        elem._e.remove_children()
        elem._e.remove_attr('id', XMLNS)
        elem._e.text = self.simple_lemmatized_edition_form
        return elem
    
    @cached_property
    def simple_lemmatized_edition_form(self) -> str:
        """
        Form for use as text in the simple_lemmatized_edition_element
        """
        return self.normalized_form

    @cached_property
    def normalized_form(self) -> str:
        """
        Returns the normalized form of the token, i.e.
        taking the text from <reg> not <orig>, <corr> not <sic>;
        also excludes text from <g>.
        Compare @form and @orig_form
        """
        
        if self.representable_cls_inst is None:
            return self._e.text_desc
        if type(self.representable_cls_inst) is type(self):
            raise TypeError(f'Class {type(self)} must implement property `normalized_form`.')
        return self.representable_cls_inst.normalized_form
    
    @cached_property
    def orig_form(self) -> str:
        """
        Returns the original form of the token, i.e.
        taking the text from <reg> not <orig>, <corr> not <sic>;
        also excludes text from <g>.
        Compare @form and @normalized_form
        """
        non_ancestors = RegTextType.values()

        ancestors_str = ' and '.join([f'not(ancestor::ns:{ancestor})' 
                                 for ancestor in non_ancestors])

        normalized_text = self._e.xpath(f'descendant::text()[{ancestors_str}]')
        return self._e._clean_text(''.join([str(t) for t in normalized_text]))
    
    @property
    def representable_cls_inst(self) -> RepresentableElement | None:
        """
        An instance of a class inheriting from Representable giving 
        behaviours specific to the element in question, e.g. W, G, Expan etc.
        """

        cls = self.elem_classes.get(self._e.localname)
        if cls is None:
            return None
        inst = cls(self._e)
        return inst

    @property
    def type(self) -> str:
        return self._e.tag.name
