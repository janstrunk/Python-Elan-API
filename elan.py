# Simple Python API to access an ELAN file
#
# Jan Strunk
# June 2016

# Import libraries for handling XML
import xml.dom.minidom as dom
from xml.sax.saxutils import escape

# Regular expressions
import re

# Class to model a single ELAN time slot
class ELANTimeSlot:
    
    # ID of time slot
    ID = None
    
    # Time value of time slot (in milliseconds)
    time_value = None
    
    # Constructor
    def __init__(self, ID, time_value=None):
        self.ID = ID

        if not isinstance(time_value, int) and not time_value is None:
            time_value = int(time_value)

        self.time_value = time_value
    
    # Factory method to construct an ELANTimeSlot object
    # from a DOM xml node
    @classmethod
    def from_xml(cls, xml_node):
        
        # Make sure that the xml_node has the correct type
        if xml_node.tagName != "TIME_SLOT":
            raise RuntimeError("Cannot construct an ELANTimeSlot object from xml node of type " + xml_node.tagName)
        
        if xml_node.hasAttribute("TIME_SLOT_ID"):
            time_slot_id = xml_node.getAttribute("TIME_SLOT_ID")
        else:
            raise RuntimeError("TIME_SLOT is missing TIME_SLOT_ID attribute.")

        if xml_node.hasAttribute("TIME_VALUE"):
            time_value = int(xml_node.getAttribute("TIME_VALUE"))
        else:
            time_value = None

        # TODO: Maybe check for superfluous unknown attributes

        return cls(time_slot_id, time_value)

    # Method to produce an xml description from an ELANTimeSlot object
    def to_xml(self, indent="    "):
        
        # Construct a new xml node
        node = 2 * indent + "<TIME_SLOT "
        
        # Set TIME_SLOT_ID
        node += "TIME_SLOT_ID=\"" + escape(self.get_id()) + "\""
        
        # If the TIME_SLOT has a TIME_VALUE, output it too
        if self.has_time_value():
            node += " TIME_VALUE=\"" + escape(str(self.get_time_value())) + "\""
        
        # Close of the node
        node += "/>\n"
        
        # Return the string representation of the XML node
        return node
    
    # Getter and setter methods
    def get_id(self):
        return self.ID
    
    def get_time_value(self):
        return self.time_value
    
    def set_id(self, ID):
        self.ID = ID
    
    def set_time_value(self, time_value):
        if not isinstance(time_value, int) and not time_value is None:
            time_value = int(time_value)

        self.time_value = time_value
        
    def has_time_value(self):
        if self.time_value is not None:
            return True
        else:
            return False
    
    # Useful hooks
    
    # Assume that ID and value have to be equal
    def __eq__(self, other):
        if self.ID == other.ID and self.time_value == other.time_value:
            return True
        else:
            return False
    
    def __ne__(self, other):
        if self == other:
            return False
        else:
            return True
    
    # Only compare time values
    def __gt__(self, other):
        if self.time_value > other.time_value:
            return True
        else:
            return False
    
    def __lt__(self, other):
        if self.time_value < other.time_value:
            return True
        else:
            return False
    
    def __ge__(self, other):
        if self.time_value == other.time_value or self.time_value > other.time_value:
            return True
        else:
            return False
    
    def __le__(self, other):
        if self.time_value == other.time_value or self.time_value < other.time_value:
            return True
        else:
            return False
    
    # Add time values
    def __add__(self, other):
        return self.time_value + other.time_value
    
    # Subtract time values
    def __sub__(self, other):
        return self.time_value - other.time_value
    
    def __repr__(self):
        # Construct a readable representation
        return "[ID:\t" + self.ID + ", " + str(self.time_value) + "]"
    
    # Construct a string representation
    def __str__(self):
        return self.ID + " " + str(self.time_value)
    
    # Hash the ELANTimeSlot object
    def __hash__(self):
        return hash(self.ID + " " + str(self.time_value))

# Class to model an ELAN time order
class ELANTimeOrder:
    
    # Reference to ELAN file
    ELAN_file = None
    
    # List of time slots
    time_slots = []
    
    # Dictionary view from ids to ELANTimeSlot objects
    time_slots_dict = {}
    
    # Constructor
    def __init__(self, ELAN_file):
        self.ELAN_file = ELAN_file
        self.time_slots = []
        self.time_slots_dict = {}
    
    # Factory method to construct an ELANTimeOrder object
    # from a DOM xml node
    @classmethod
    def from_xml(cls, xml_node, ELAN_file):
        
        # Make sure that the xml_node has the correct type
        if xml_node.tagName != "TIME_ORDER":
            raise RuntimeError("Cannot construct an ELANTimeOrder object from xml node of type " + xml_node.tagName)
        
        # Make a new ELANTimeOrder object
        time_order = ELANTimeOrder(ELAN_file)
        
        # Go through time slots in time order
        for child_node in xml_node.childNodes:
            
            # Skip non-element nodes
            if child_node.nodeType != child_node.ELEMENT_NODE:
                continue
            
            # Make sure that all child nodes have the type TIME_SLOT
            if child_node.tagName != "TIME_SLOT":
                raise RuntimeError("Expected TIME_SLOT element in TIME_ORDER but found a " + child_node.tagName + " element.")
        
            # Construct a new ELANTimeSlot object
            time_slot = ELANTimeSlot.from_xml(child_node)
            
            # Add the time slot to the time order
            time_order.add_time_slot(time_slot)
        
        return time_order

    # Method to produce an xml description from an ELANTimeOrder object
    def to_xml(self, indent="    "):
        
        # Construct a new xml node
        node = indent + "<TIME_ORDER>\n"
        
        # If the ELANTimeOrder contains any time slots, output them
        if self.has_time_slots():
            
            # For every time slot
            for time_slot in self:
                
                # Add its xml node to the output
                node += time_slot.to_xml(indent=indent)
        
        # Construct the closing bracket
        node += indent + "</TIME_ORDER>\n"

        # Return the string representation of the XML node
        return node
    
    def get_time_slots(self):
        return self.time_slots
    
    def get_time_slots_dict(self):
        return self.time_slots_dict
    
    def get_time_slot_by_id(self, ID):
        if ID in self.time_slots_dict:
            return self.time_slots_dict[ID]
        else:
            raise KeyError("No ELANTimeSlot with the given ID found.")
    
    def get_time_slot_by_position(self, position):
        return self.time_slots[position]
    
    def has_time_slots(self):
        if len(self.time_slots) > 0:
            return True
        else:
            return False
    
    # Append a time slot to the time order
    def add_time_slot(self, time_slot):
        
        # Make sure it really is an ELANTimeSlot object
        if isinstance(time_slot, ELANTimeSlot):
            
            # Make sure the ID is not used yet
            if time_slot in self:
                raise KeyError("Cannot append time_slot. ID is already in use.")
            
            else:
                self.time_slots.append(time_slot)
                self.time_slots_dict[time_slot.get_id()] = time_slot
        
        else:
            raise TypeError("Can only append an ELANTimeSlot object to the time order.")
    
    # Useful hooks
    
    # Overload the in operator (only consider the ID)
    def __contains__(self, time_slot):
        
        if time_slot.get_id() in self.time_slots_dict:
            return True
        else:
            return False
    
    # Iterator for the list of time slots
    def __iter__(self):
        return iter(self.time_slots)
    
    # Returns the number of time slots contained in the time order
    def __len__(self):
        return len(self.time_slots)

    # TODO: Add methods to insert or delete time slots


# Class to model a single ELAN media descriptor
class ELANMediaDescriptor:
    
    # Attributes
    media_url = None            # required
    relative_media_url = None   # optional
    mime_type = None            # required
    time_origin = None          # optional
    extracted_from = None       # optional
    
    # Constructor
    def __init__(self, media_url, mime_type, relative_media_url = None, time_origin = None, extracted_from = None):
        self.media_url = media_url
        self.mime_type = mime_type
        self.relative_media_url = relative_media_url
        self.time_origin = time_origin
        self.extracted_from = extracted_from

    # Factory method to construct an ELANMediaDescriptor object
    # from a DOM xml node
    @classmethod
    def from_xml(cls, xml_node):
        
        # Make sure that the xml_node has the correct type
        if xml_node.tagName != "MEDIA_DESCRIPTOR":
            raise RuntimeError("Cannot construct an ELANMediaDescriptor object from xml node of type " + xml_node.tagName)

        if xml_node.hasAttribute("MEDIA_URL"):
            media_url = xml_node.getAttribute("MEDIA_URL")
        else:
            raise RuntimeError("MEDIA_DESCRIPTOR is missing MEDIA_URL attribute.")
        
        if xml_node.hasAttribute("RELATIVE_MEDIA_URL"):
            relative_media_url = xml_node.getAttribute("RELATIVE_MEDIA_URL")
        else:
            relative_media_url = None
        
        if xml_node.hasAttribute("MIME_TYPE"):
            mime_type = xml_node.getAttribute("MIME_TYPE")
        else:
            raise RuntimeError("MEDIA_DESCRIPTOR is missing MIME_TYPE attribute.")

        if xml_node.hasAttribute("TIME_ORIGIN"):
            time_origin = xml_node.getAttribute("TIME_ORIGIN")
        else:
            time_origin = None

        if xml_node.hasAttribute("EXTRACTED_FROM"):
            extracted_from = xml_node.getAttribute("EXTRACTED_FROM")
        else:
            extracted_from = None

        # TODO: Maybe check for superfluous unknown attributes

        return cls(media_url, mime_type, relative_media_url, time_origin, extracted_from)

    # Method to produce an xml description from an ELANMediaDescriptor object
    def to_xml(self, indent="    "):
        
        # Construct a new xml node
        node = 2 * indent + "<MEDIA_DESCRIPTOR "
        
        # Set MEDIA_URL
        node += "MEDIA_URL=\"" + escape(self.get_media_url()) + "\""
        
        # Set RELATIVE_MEDIA_URL if there is one
        if self.has_relative_media_url():
            node += " RELATIVE_MEDIA_URL=\"" + escape(self.get_relative_media_url()) + "\""
        
        # Set the MIME_TYPE
        node += " MIME_TYPE=\"" + escape(self.get_mime_type()) + "\""
        
        # Set the TIME_ORIGIN if there is one
        if self.has_time_origin():
            node += " TIME_ORIGIN=\"" + escape(self.get_time_origin()) + "\""
        
        # Set the EXTRACTED_FROM attribute if there is one
        if self.has_extracted_from():
            node += " EXTRACTED_FROM=\"" + escape(self.get_extracted_from()) + "\""
        
        # Close of the node
        node += "/>\n"
        
        # Return the string representation of the XML node
        return node

    # Getter and setter methods
    def get_media_url(self):
        return self.media_url
    
    def get_relative_media_url(self):
        return self.relative_media_url
    
    def get_mime_type(self):
        return self.mime_type
    
    def get_time_origin(self):
        return self.time_origin
    
    def get_extracted_from(self):
        return self.extracted_from
    
    def set_media_url(self, media_url):
        self.media_url = media_url
    
    def set_relative_media_url(self, relative_media_url):
        self.relative_media_url = relative_media_url
    
    def set_mime_type(self, mime_type):
        self.mime_type = mime_type
    
    def set_time_origin(self, time_origin):
        self.time_origin = time_origin
        
    def set_extracted_from(self, extracted_from):
        self.extracted_from = extracted_from
    
    def has_relative_media_url(self):
        if self.relative_media_url is not None:
            return True
        else:
            return False
    
    def has_time_origin(self):
        if self.time_origin is not None:
            return True
        else:
            return False

    def has_extracted_from(self):
        if self.extracted_from is not None:
            return True
        else:
            return False

    # TODO: Add sanity checks!
    
    # Useful hooks
    def __eq__(self, other):
        if self.media_url == other.media_url and self.relative_media_url == other.relative_media_url and self.mime_type == other.mime_type and self.time_origin == other.time_origin and self.extracted_from == other.extracted_from:
            return True
        else:
            return False
    
    def __ne__(self, other):
        if self == other:
            return False
        else:
            return True
    
    def __hash__(self):
        return hash(self.media_url + " " + self.mime_type)


# Class to model a single ELAN linked file descriptor
class ELANLinkedFileDescriptor:
    
    # Attributes
    link_url = None             # required
    relative_link_url = None    # optional
    mime_type = None            # required
    time_origin = None          # optional
    associated_with = None      # optional

    # Constructor
    def __init__(self, link_url, mime_type, relative_link_url = None, time_origin = None, associated_with = None):
        self.link_url = link_url
        self.mime_type = mime_type
        self.relative_link_url = relative_link_url
        self.time_origin = time_origin
        self.associated_with = associated_with

    # Factory method to construct an ELANLinkedFileDescriptor object
    # from a DOM xml node
    @classmethod
    def from_xml(cls, xml_node):
        
        # Make sure that the xml_node has the correct type
        if xml_node.tagName != "LINKED_FILE_DESCRIPTOR":
            raise RuntimeError("Cannot construct an ELANLinkedFileDescriptor object from xml node of type " + xml_node.tagName)

        if xml_node.hasAttribute("LINK_URL"):
            link_url = xml_node.getAttribute("LINK_URL")
        else:
            raise RuntimeError("LINKED_FILE_DESCRIPTOR is missing LINK_URL attribute.")
        
        if xml_node.hasAttribute("RELATIVE_LINK_URL"):
            relative_link_url = xml_node.getAttribute("RELATIVE_LINK_URL")
        else:
            relative_link_url = None
        
        if xml_node.hasAttribute("MIME_TYPE"):
            mime_type = xml_node.getAttribute("MIME_TYPE")
        else:
            raise RuntimeError("LINKED_FILE_DESCRIPTOR is missing MIME_TYPE attribute.")

        if xml_node.hasAttribute("TIME_ORIGIN"):
            time_origin = xml_node.getAttribute("TIME_ORIGIN")
        else:
            time_origin = None

        if xml_node.hasAttribute("ASSOCIATED_WITH"):
            associated_with = xml_node.getAttribute("ASSOCIATED_WITH")
        else:
            associated_with = None
        
        # TODO: Maybe check for superfluous unknown attributes

        return cls(link_url, mime_type, relative_link_url, time_origin, associated_with)

    # Method to produce an xml description from an ELANLinkedFileDescriptor object
    def to_xml(self, indent="    "):
        
        # Construct a new xml node
        node = 2 * indent + "<LINKED_FILE_DESCRIPTOR "
        
        # Set LINK_URL
        node += "LINK_URL=\"" + escape(self.get_link_url()) + "\""
        
        # Set RELATIVE_LINK_URL if there is one
        if self.has_relative_link_url():
            node += " RELATIVE_LINK_URL=\"" + escape(self.get_relative_link_url()) + "\""
        
        # Set the MIME_TYPE
        node += " MIME_TYPE=\"" + escape(self.get_mime_type()) + "\""
        
        # Set the TIME_ORIGIN if there is one
        if self.has_time_origin():
            node += " TIME_ORIGIN=\"" + escape(self.get_time_origin()) + "\""
        
        # Set the EXTRACTED_FROM attribute if there is one
        if self.has_associated_with():
            node += " ASSOCIATED_WITH=\"" + escape(self.get_associated_with()) + "\""
        
        # Close of the node
        node += "/>\n"
        
        # Return the string representation of the XML node
        return node
    
    # Getter and setter methods
    def get_link_url(self):
        return self.link_url
    
    def get_relative_link_url(self):
        return self.relative_link_url
    
    def get_mime_type(self):
        return self.mime_type
    
    def get_time_origin(self):
        return self.time_origin
    
    def get_associated_with(self):
        return self.associated_with
    
    def set_link_url(self, link_url):
        self.link_URL = link_url
    
    def set_relative_link_url(self, relative_link_url):
        self.relative_link_url = relative_link_url
    
    def set_mime_type(self, mime_type):
        self.mime_type = mime_type
    
    def set_time_origin(self, time_origin):
        self.time_origin = time_origin
        
    def set_associated_with(self, associated_with):
        self.associated_with = associated_with
    
    # TODO: Add sanity checks!
    
    # Useful hooks
    def __eq__(self, other):
        if self.link_url == other.link_url and self.relative_link_url == other.relative_link_url and self.mime_type == other.mime_type and self.time_origin == other.time_origin and self.associated_with == other.associated_with:
            return True
        else:
            return False
    
    def __ne__(self, other):
        if self == other:
            return False
        else:
            return True
    
    def __hash__(self):
        return hash(self.link_url + " " + self.mime_type)


# Class to model a single ELAN annotation
class ELANAnnotation:

    # Reference to the ELANFile
    ELAN_file = None
    
    # Reference to the ELANTier
    tier = None
    
    # ID
    annotation_id = None        # Required
    
    # Value of the annotation
    annotation_value = None     # Required
    
    # Annotation type
    annotation_type = None      # Required, set by the subclasses

    # External reference
    external_ref = None         # Optional
    
    # Getter and setter methods
    def get_ELAN_file(self):
        return self.ELAN_file
    
    def get_tier(self):
        return self.tier
    
    def get_annotation_id(self):
        return self.annotation_id
    
    def get_annotation_value(self):
        return self.annotation_value
    
    def get_annotation_type(self):
        return self.annotation_type

    def get_external_ref(self):
        return self.external_ref
    
    def set_ELAN_file(self, ELAN_file):
        self.ELAN_file = ELAN_file
    
    def set_tier(self, tier):
        self.tier = tier
    
    def set_annotation_id(self, annotation_id):
        self.annotation_id = annotation_id
    
    def set_annotation_value(self, annotation_value):
        self.annotation_value = annotation_value

    def set_external_ref(self, external_ref):
        self.external_ref = external_ref
    
    def has_external_ref(self):
        if self.external_ref is not None:
            return True
        else:
            return False
    
    def is_empty(self):
        if self.annotation_value is None or self.annotation_value == "":
            return True
        else:
            return False


# Class to model a single ELAN alignable annotation
class ELANAlignableAnnotation(ELANAnnotation):
    
    # Type of annotation
    annotation_type = "Alignable_Annotation"
    
    # Value of the annotation
    annotation_value = ""
    
    # References to the time order
    start_time_slot = None      # Required
    end_time_slot = None        # Required
    
    # External references
    svg_ref = None              # Optional
    
    # Constructor
    def __init__(self, annotation_id, annotation_value, start_time_slot, end_time_slot, ELAN_file, tier, svg_ref = None, external_ref = None):
        self.annotation_id = annotation_id
        self.annotation_value = annotation_value
        self.start_time_slot = start_time_slot
        self.end_time_slot = end_time_slot
        self.ELAN_file = ELAN_file
        self.tier = tier
        self.svg_ref = svg_ref

    # Factory method to construct an ELANAlignableAnnotation object
    # from a DOM xml node
    @classmethod
    def from_xml(cls, xml_node, ELAN_file, tier):
        
        # Make sure that the xml_node has the correct type
        if xml_node.tagName != "ALIGNABLE_ANNOTATION":
            raise RuntimeError("Cannot construct an ELANAlignableAnnotation object from xml node of type " + xml_node.tagName)

        if xml_node.hasAttribute("ANNOTATION_ID"):
            annotation_id = xml_node.getAttribute("ANNOTATION_ID")
        else:
            raise RuntimeError("ALIGNABLE_ANNOTATION is missing ANNOTATION_ID attribute.")
        
        if xml_node.hasAttribute("TIME_SLOT_REF1"):
            time_slot_ref1 = xml_node.getAttribute("TIME_SLOT_REF1")
        else:
            raise RuntimeError("ALIGNABLE_ANNOTATION is missing TIME_SLOT_REF1 attribute.")

        if xml_node.hasAttribute("TIME_SLOT_REF2"):
            time_slot_ref2 = xml_node.getAttribute("TIME_SLOT_REF2")
        else:
            raise RuntimeError("ALIGNABLE_ANNOTATION is missing TIME_SLOT_REF2 attribute.")

        if xml_node.hasAttribute("SVG_REF"):
            svg_ref = xml_node.getAttribute("SVG_REF")
        else:
            svg_ref = None

        if xml_node.hasAttribute("EXTERNAL_REF"):
            external_ref = xml_node.getAttribute("EXTERNAL_REF")
        else:
            external_ref = None
            
        # Extract value of daughter element ANNOTATION_VALUE
        child_node = xml_node.firstChild
        
        # Only consider element nodes
        while child_node.nodeType != child_node.ELEMENT_NODE and child_node.nextSibling is not None:
            child_node = child_node.nextSibling
        
        # Make sure that the child node has the correct type
        if child_node.tagName != "ANNOTATION_VALUE":
            raise RuntimeError("Expected ANNOTATION_VALUE element in ALIGNABLE_ANNOTATION but found a " + child_node.tagName + " element.")
        
        if child_node.hasChildNodes():
            
            if child_node.firstChild.nodeType == child_node.TEXT_NODE:
                annotation_value = child_node.firstChild.data
            else:
                annotation_value = ""
        else:
            annotation_value = ""

        # TODO: Maybe check for superfluous unknown attributes
        
        # Construct a new ELANAlignableAnnotation
        return cls(annotation_id, annotation_value, time_slot_ref1, time_slot_ref2, ELAN_file, tier, svg_ref, external_ref)

    # Method to produce an xml description from an ELANAlignableAnnotation object
    def to_xml(self, indent="    "):
        
        # Construct a new xml node
        node = 2 * indent + "<ANNOTATION>\n"
        
        # Add the inner ALIGNABLE_ANNOTATION node
        node += 3 * indent + "<ALIGNABLE_ANNOTATION"
        
        # Set ANNOTATION_ID
        node += " ANNOTATION_ID=\"" + escape(self.get_annotation_id()) + "\""
        
        # Set TIME_SLOT_REF1
        node += " TIME_SLOT_REF1=\"" + escape(self.get_start_time_slot()) + "\""

        # Set TIME_SLOT_REF2
        node += " TIME_SLOT_REF2=\"" + escape(self.get_end_time_slot()) + "\""
        
        # Set the SVG_REF if there is one
        if self.has_svg_ref():
            node += " SVG_REF=\"" + escape(self.get_svg_ref()) + "\""

        # Set the EXT_REF if there is one
        if self.has_external_ref():
            node += " EXT_REF=\"" + escape(self.get_external_ref()) + "\""
        
        # Close the ALIGNABLE_ANNOTATION start tag
        node += ">\n"
        
        # Add the ANNOTATION_VALUE
        if not self.is_empty():
            node += 4 * indent + "<ANNOTATION_VALUE>" + escape(self.get_annotation_value()) + "</ANNOTATION_VALUE>\n"
        else:
            node += 4 * indent + "<ANNOTATION_VALUE></ANNOTATION_VALUE>\n"
        
        # Close off the ALIGNABLE_ANNOTATION node
        node += 3 * indent + "</ALIGNABLE_ANNOTATION>\n"
        
        # Close off the ANNOTATION node
        node += 2 * indent + "</ANNOTATION>\n"
        
        # Return the string representation of the XML node
        return node

    # Getter and setter methods
    def get_start_time_slot(self):
        return self.start_time_slot
    
    def get_end_time_slot(self):
        return self.end_time_slot
    
    def get_svg_ref(self):
        return self.svg_ref
    
    def set_start_time_slot(self, start_time_slot):
        self.start_time_slot = start_time_slot
        
    def set_end_time_slot(self, end_time_slot):
        self.end_time_slot = end_time_slot
    
    def set_svg_ref(self, svg_ref):
        self.svg_ref = svg_ref
    
    def get_start_time(self):
        time_slot = self.ELAN_file.time_order.get_time_slot_by_id(self.start_time_slot)
        return time_slot.get_time_value()
    
    def get_end_time(self):
        time_slot = self.ELAN_file.time_order.get_time_slot_by_id(self.end_time_slot)
        return time_slot.get_time_value()
    
    def has_svg_ref(self):
        if self.svg_ref is not None:
            return True
        else:
            return False
    
    def has_annotation_value(self):
        if self.annotation_value == "":
            return False
        else:
            return True
    
    # Useful hooks
    def __len__(self):
        
        # Calculate length in milliseconds
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        
        # Length is absolute difference
        return abs(end_time - start_time)
    
    def __contains__(self, other):
        
        # For strings test whether they are contained
        # in the annotation value
        if type(other) == "str":
            
            if other in self.value:
                return True
            else:
                return False
        
        # For alignable annotations, test whether they
        # are contained in the time interval of self
        elif type(other) == "ELANAlignableAnnotation":
            
            if self.get_start_time() < other.get_start_time() and self.get_end_time() > other.get_end_time():
                return True
            else:
                return False
        
        else:
            return False
    
    # Temporal equality
    def __eq__(self, other):
        if self.get_start_time() == other.get_start_time() and self.get_end_time() == other.get_end_time():
            return True
        else:
            return False
    
    def __ne__(self, other):
        if self == other:
            return False
        else:
            return True
    
    # Temporal precedence, overlaps allowed
    # TODO: Leads to problems when sorting
    def __lt__(self, other):
        if self.get_start_time() < other.get_start_time() and self.get_end_time() <= other.get_start_time():
            return True
        else:
            return False
    
    def __gt__(self, other):
        if self.get_start_time() >= other.get_end_time() and self.get_start_time() > other.get_start_time():
            return True
        else:
            return False
    
    # TODO:
    # precedes, follows (maybe use << and >>)
    # precedence with overlap
    

# Class to model a single ELAN reference annotation
class ELANRefAnnotation(ELANAnnotation):
    
    annotation_type = "Ref_Annotation"

    # Annotation value
    annotation_value = ""
    
    # Annotation reference
    annotation_ref = None       # Required
    previous_annotation = None  # Optional
    
    # Constructor
    def __init__(self, annotation_id, annotation_value, annotation_ref, ELAN_file, tier, previous_annotation=None, external_ref = None):
        self.annotation_id = annotation_id
        self.annotation_value = annotation_value
        self.annotation_ref = annotation_ref
        self.ELAN_file = ELAN_file
        self.tier = tier
        self.previous_annotation = previous_annotation
        self.external_ref = external_ref

    # Factory method to construct an ELANRefAnnotation object
    # from a DOM xml node
    @classmethod
    def from_xml(cls, xml_node, ELAN_file, tier):
        
        # Make sure that the xml_node has the correct type
        if xml_node.tagName != "REF_ANNOTATION":
            raise RuntimeError("Cannot construct an ELANRefAnnotation object from xml node of type " + xml_node.tagName)

        if xml_node.hasAttribute("ANNOTATION_ID"):
            annotation_id = xml_node.getAttribute("ANNOTATION_ID")
        else:
            raise RuntimeError("ALIGNABLE_ANNOTATION is missing ANNOTATION_ID attribute.")
        
        if xml_node.hasAttribute("ANNOTATION_REF"):
            annotation_ref = xml_node.getAttribute("ANNOTATION_REF")
        else:
            raise RuntimeError("REF_ANNOTATION is missing ANNOTATION_REF attribute.")

        if xml_node.hasAttribute("PREVIOUS_ANNOTATION"):
            previous_annotation = xml_node.getAttribute("PREVIOUS_ANNOTATION")
        else:
            previous_annotation = None

        if xml_node.hasAttribute("EXTERNAL_REF"):
            external_ref = xml_node.getAttribute("EXTERNAL_REF")
        else:
            external_ref = None

        # Extract value of daughter element ANNOTATION_VALUE
        child_node = xml_node.firstChild
        
        # Only consider element nodes
        while child_node.nodeType != child_node.ELEMENT_NODE and child_node.nextSibling is not None:
            child_node = child_node.nextSibling
        
        # Make sure that the child node has the correct type
        if child_node.tagName != "ANNOTATION_VALUE":
            raise RuntimeError("Expected ANNOTATION_VALUE element in REF_ANNOTATION but found a " + child_node.tagName + " element.")
        
        if child_node.hasChildNodes():
            
            if child_node.firstChild.nodeType == child_node.TEXT_NODE:
                annotation_value = child_node.firstChild.data
            else:
                annotation_value = ""
        else:
            annotation_value = ""

        # TODO: Maybe check for superfluous unknown attributes
        
        # Construct a new ELANRefAnnotation
        return cls(annotation_id, annotation_value, annotation_ref, ELAN_file, tier, previous_annotation, external_ref)

    # Method to produce an xml description from an ELANRefAnnotation object
    def to_xml(self, indent="    "):
        
        # Construct a new xml node
        node = 2 * indent + "<ANNOTATION>\n"
        
        # Add the inner ALIGNABLE_ANNOTATION node
        node += 3 * indent + "<REF_ANNOTATION"

        # Set ANNOTATION_ID
        node += " ANNOTATION_ID=\"" + escape(self.get_annotation_id()) + "\""
        
        # Set ANNOTATION_REF
        node += " ANNOTATION_REF=\"" + escape(self.get_annotation_ref()) + "\""

        # Set PREVIOUS_ANNOTATION if there is one
        if self.has_previous_annotation():
            node += " PREVIOUS_ANNOTATION=\"" + escape(self.get_previous_annotation_ref()) + "\""
        
        # Set the EXT_REF if there is one
        if self.has_external_ref():
            node += " EXT_REF=\"" + escape(self.get_external_ref()) + "\""
        
        # Close the ALIGNABLE_ANNOTATION start tag
        node += ">\n"
        
        # Add the ANNOTATION_VALUE
        if not self.is_empty():
            node += 4 * indent + "<ANNOTATION_VALUE>" + escape(self.get_annotation_value()) + "</ANNOTATION_VALUE>\n"
        else:
            node += 4 * indent + "<ANNOTATION_VALUE></ANNOTATION_VALUE>\n"
        
        # Close off the REF_ANNOTATION node
        node += 3 * indent + "</REF_ANNOTATION>\n"
        
        # Close off the ANNOTATION node
        node += 2 * indent + "</ANNOTATION>\n"
        
        # Return the string representation of the XML node
        return node
    
    # Getter and setter methods
    def get_annotation_ref(self):
        return self.annotation_ref
        
    def get_previous_annotation_ref(self):
        return self.previous_annotation
    
    def set_annotation_ref(self, annotation_ref):
        self.annotation_ref = annotation_ref
    
    def set_previous_annotation_ref(self, previous_annotation):
        self.previous_annotation = previous_annotation

    def get_parent_annotation(self):
        return self.ELAN_file.get_annotation_by_id(self.annotation_ref)

    def get_previous_annotation(self):
        return self.ELAN_file.get_annotation_by_id(self.previous_annotation_ref)
    
    def has_previous_annotation(self):
        if self.previous_annotation is not None:
            return True
        else:
            return False
    
    def has_annotation_value(self):
        if self.annotation_value != "":
            return True
        else:
            return False


# Class to model a single ELAN tier
class ELANTier:

    # Reference to the ELANFile
    ELAN_file = None
    
    # Attributes
    tier_id = None          # Required
    participant = None      # Optional
    annotator = None        # Optional
    linguistic_type = None  # Required
    default_locale = None   # Optional
    parent_tier_ref = None      # Optional

    # List of annotations
    annotations = []
    
    # Constructor
    def __init__(self, tier_id, linguistic_type, ELAN_file, participant = None, annotator = None, default_locale = None, parent_tier_ref = None):
        self.tier_id = tier_id
        self.linguistic_type = linguistic_type
        self.ELAN_file = ELAN_file
        self.participant = participant
        self.annotator = annotator
        self.default_locale = default_locale
        self.parent_tier_ref = parent_tier_ref
        
        self.annotations = []
        self.annotations_dict = {}

    # Factory method to construct an ELANTier object
    # from a DOM xml node
    @classmethod
    def from_xml(cls, xml_node, ELAN_file):
        
        # Make sure that the xml_node has the correct type
        if xml_node.tagName != "TIER":
            raise RuntimeError("Cannot construct an ELANTier object from xml node of type " + xml_node.tagName)
        
        if xml_node.hasAttribute("TIER_ID"):
            tier_id = xml_node.getAttribute("TIER_ID")
        else:
            raise RuntimeError("TIER is missing TIER_ID attribute.")

        if xml_node.hasAttribute("PARTICIPANT"):
            participant = xml_node.getAttribute("PARTICIPANT")
        else:
            participant = None
        
        if xml_node.hasAttribute("ANNOTATOR"):
            annotator = xml_node.getAttribute("ANNOTATOR")
        else:
            annotator = None

        if xml_node.hasAttribute("LINGUISTIC_TYPE_REF"):
            linguistic_type_ref = xml_node.getAttribute("LINGUISTIC_TYPE_REF")
        else:
            raise RuntimeError("TIER is missing LINGUISTIC_TYPE_REF attribute.")
        
        if xml_node.hasAttribute("DEFAULT_LOCALE"):
            default_locale = xml_node.getAttribute("DEFAULT_LOCALE")
        else:
            default_locale = None

        if xml_node.hasAttribute("PARENT_REF"):
            parent_ref = xml_node.getAttribute("PARENT_REF")
        else:
            parent_ref = None

        # TODO: Maybe check for superfluous unknown attributes
        
        # Construct a new tier
        tier = cls(tier_id, linguistic_type_ref, ELAN_file, participant, annotator, default_locale, parent_ref)
        
        # Add annotations to it
        # Go through time slots in time order
        for child_node in xml_node.childNodes:
            
            # Skip all non-element nodes
            if child_node.nodeType != child_node.ELEMENT_NODE:
                continue
            
            # Make sure that all child nodes have the type TIME_SLOT
            if child_node.tagName != "ANNOTATION":
                raise RuntimeError("Expected ANNOTATION element in TIER but found a " + child_node.tagName + " element.")
            
            # Get the first and only child of the ANNOTATION element
            grand_child_node = child_node.firstChild
            while grand_child_node.nodeType != grand_child_node.ELEMENT_NODE and grand_child_node.nextSibling is not None:
                grand_child_node = grand_child_node.nextSibling
            
            # Make sure that the grand child node is an ALIGNABLE_ANNOTATION or a REF_ANNOTATION
            if grand_child_node.tagName == "ALIGNABLE_ANNOTATION":
                
                # Construct a new ELANAlignableAnnotation
                alignable_annotation = ELANAlignableAnnotation.from_xml(grand_child_node, ELAN_file, tier)
                
                # Add the annotation to the tier
                tier.add_annotation(alignable_annotation)
            
            elif grand_child_node.tagName == "REF_ANNOTATION":
                
                # Construct a new ELANRefAnnotation
                ref_annotation = ELANRefAnnotation.from_xml(grand_child_node, ELAN_file, tier)
                
                # Add the annotation to the tier
                tier.add_annotation(ref_annotation)
            
            else:
                raise RuntimeError("Expected ALIGNABLE_ANNOTATION or REF_ANNOTATION element in ANNOTATION but found a " + child_node.tagName + " element.")        

        # Return the complete ELANTier object
        return tier

    # Method to produce an xml description from an ELANTier object
    def to_xml(self, indent="    "):

        # Construct a new xml node
        node = indent + "<TIER"
        
        # Add TIER_ID
        node += " TIER_ID=\"" + escape(self.get_tier_id()) + "\""
        
        # Add PARTICIPANT if there is one
        if self.has_participant():
            node += " PARTICIPANT=\"" + escape(self.get_participant()) + "\""

        # Add ANNOTATOR if there is one
        if self.has_annotator():
            node += " ANNOTATOR=\"" + escape(self.get_annotator()) + "\""

        # Set LINGUISTIC_TYPE_REF
        node += " LINGUISTIC_TYPE_REF=\"" + escape(self.get_linguistic_type()) + "\""
        
        # Set DEFAULT_LOCALE if there is one
        if self.has_default_locale():
            node += " DEFAULT_LOCALE=\"" + escape(self.get_default_locale()) + "\""

        # Set PARENT_REF if there is one
        if self.has_parent_tier_ref():
            node += " PARENT_REF=\"" + escape(self.get_parent_tier_ref()) + "\""

        # Close the TIER start tag
        node += ">\n"
        
        # Insert annotation values
        for annotation in self:
            
            node += annotation.to_xml(indent=indent)
        
        # Close off the TIER node
        node += indent + "</TIER>\n"
        
        # Return the string representation of the XML node
        return node
    
    # Getter and setter methods
    def get_tier_id(self):
        return self.tier_id
    
    def get_linguistic_type(self):
        return self.linguistic_type
    
    def get_ELAN_file(self):
        return self.ELAN_file
    
    def get_participant(self):
        return self.participant
    
    def get_annotator(self):
        return self.annotator
    
    def get_default_locale(self):
        return self.default_locale
    
    def get_parent_tier_ref(self):
        return self.parent_tier_ref
    
    def get_parent_tier(self):
        return self.ELAN_file.get_tier_by_id(self.parent_tier_ref)
    
    def get_annotations(self):
        return self.annotations
    
    def set_tier_id(self, tier_id):
        self.tier_id = tier_id
        
    def set_linguistic_type(self, linguistic_type):
        self.linguistic_type = linguistic_type
    
    def set_ELAN_file(self, ELAN_file):
        self.ELAN_file = ELAN_file
    
    def set_participant(self, participant):
        self.participant = participant
    
    def set_annotator(self, annotator):
        self.annotator
    
    def set_default_locale(self, default_locale):
        self.default_locale = default_locale
    
    def set_parent_tier_ref(self, parent_tier_ref):
        self.parent_tier_ref = parent_tier_ref
    
    def add_annotation(self, annotation):
        self.annotations.append(annotation)
    
    def has_participant(self):
        if self.participant is not None:
            return True
        else:
            return False

    def has_annotator(self):
        if self.annotator is not None:
            return True
        else:
            return False

    def has_default_locale(self):
        if self.default_locale is not None:
            return True
        else:
            return False

    def has_parent_tier_ref(self):
        if self.parent_tier_ref is not None:
            return True
        else:
            return False
    
    def has_annotations(self):
        if len(self.annotations) > 0:
            return True
        else:
            return False
    
    def is_empty(self):
        if len(self.annotations) == 0:
            return True
        else:
            return False
    
    # Useful hooks
    
    # Number of annotations on the tier
    def __len__(self):
        return len(self.annotations)
    
    # Iterator
    def __iter__(self):
        return iter(self.annotations)
    
    # in operator
    def __contains__(self, annotation):
        if annotation.get_id() in self.annotations_dict:
            return True
        else:
            return False


# Class to model an ELAN linguistic type
class ELANLinguisticType:
    
    # Reference to the ELAN file
    ELAN_file = None
    
    # Attributes
    linguistic_type_id = None           # Required
    time_alignable = None               # Optional
    constraints = None                  # Optional
    graphic_references = None           # Optional
    controlled_vocabulary_ref = None    # Optional
    external_ref = None                 # Optional
    lexicon_ref = None                  # Optional

    # Constructor
    def __init__(self, ID, ELAN_file, time_alignable=None, constraints=None, graphic_ref=None, cv_ref=None, external_ref=None, lexicon_ref=None):
        self.linguistic_type_id = ID
        self.ELAN_file = ELAN_file
        self.constraints = constraints
        self.graphic_references = graphic_ref
        self.controlled_vocabulary_ref = cv_ref
        self.external_ref = external_ref
        self.lexicon_ref = lexicon_ref

        if self.constraints is None:
            if time_alignable == "true":
                self.time_alignable = True
            elif time_alignable == "false":
                self.time_alignable = False
            else:
                raise RuntimeError("Illegal value " + str(time_alignable) + " of attribute TIME_ALIGNABLE in LINGUISTIC_TYPE element.")
        
        elif self.constraints == "None":
            self.time_alignable = True
        elif self.constraints == "Time_Subdivision":
            self.time_alignable = True
        elif self.constraints == "Symbolic_Subdivision":
            self.time_alignable = False
        elif self.constraints == "Symbolic_Association":
            self.time_alignable = False
        elif self.constraints == "Included_In":
            self.time_alignable = True
        else:
            raise RuntimeError("Unknown constraint: " + self.constraints)            

    # Factory method to construct an ELANLinguisticType object
    # from a DOM xml node
    @classmethod
    def from_xml(cls, xml_node, ELAN_file):
        
        # Make sure that the xml_node has the correct type
        if xml_node.tagName != "LINGUISTIC_TYPE":
            raise RuntimeError("Cannot construct an ELANLinguisticType object from xml node of type " + xml_node.tagName)

        if xml_node.hasAttribute("LINGUISTIC_TYPE_ID"):
            linguistic_type_id = xml_node.getAttribute("LINGUISTIC_TYPE_ID")
        else:
            raise RuntimeError("LINGUISTIC_TYPE is missing LINGUISTIC_TYPE_ID attribute.")
        
        if xml_node.hasAttribute("TIME_ALIGNABLE"):
            time_alignable = xml_node.getAttribute("TIME_ALIGNABLE")
        else:
            time_alignable = None
        
        if xml_node.hasAttribute("CONSTRAINTS"):
            constraints = xml_node.getAttribute("CONSTRAINTS")
        else:
            constraints = None

        if xml_node.hasAttribute("GRAPHIC_REFERENCES"):
            graphic_ref = xml_node.getAttribute("GRAPHIC_REFERENCES")
        else:
            graphic_ref = None

        if xml_node.hasAttribute("CONTROLLED_VOCABULARY_REF"):
            cv_ref = xml_node.getAttribute("CONTROLLED_VOCABULARY_REF")
        else:
            cv_ref = None

        if xml_node.hasAttribute("EXT_REF"):
            ext_ref = xml_node.getAttribute("EXT_REF")
        else:
            ext_ref = None

        if xml_node.hasAttribute("LEXICON_REF"):
            lexicon_ref = xml_node.getAttribute("LEXICON_REF")
        else:
            lexicon_ref = None
        
        # TODO: Maybe check for superfluous unknown attributes

        return cls(linguistic_type_id, ELAN_file, time_alignable, constraints, graphic_ref, cv_ref, ext_ref, lexicon_ref)

    # Method to produce an xml description from an ELANLinguisticType object
    def to_xml(self, indent="    "):

        # Construct a new xml node
        node = indent + "<LINGUISTIC_TYPE"
        
        # Add LINGUISTIC_TYPE_ID
        node += " LINGUISTIC_TYPE_ID=\"" + escape(self.get_linguistic_type_id()) + "\""
        
        # Add TIME_ALIGNABLE flag if there is one
        if self.has_time_alignable_flag():
            
            if self.is_time_alignable():
                
                node += " TIME_ALIGNABLE=\"true\""
            
            else:
                
                node += " TIME_ALIGNABLE=\"false\""
        
        # Add CONSTRAINTS attribute if there is one
        if self.has_constraints():
            
            node += " CONSTRAINTS=\"" + escape(self.get_constraints()) + "\""
        
        # Add GRAPHIC_REFERENCES attribute if there is one
        if self.has_graphic_references_flag():
            
            if self.has_graphic_references():
                
                node += " GRAPHIC_REFERENCES=\"true\""
            
            else:
                
                node += " GRAPHIC_REFERENCES=\"false\""
        
        # Add CONTROLLED_VOCABULARY_REF if there is one
        if self.has_controlled_vocabulary_ref():
            
            node += " CONTROLLED_VOCABULARY_REF=\"" + escape(self.get_controlled_vocabulary_ref()) + "\""
        
        # Add EXT_REF if there is one
        if self.has_external_ref():
            
            node += " EXT_REF=\"" + escape(self.get_external_ref()) + "\""

        # Add LEXICON_REF if there is one
        if self.has_lexicon_ref():
            
            node += " LEXICON_REF=\"" + escape(self.get_lexicon_ref()) + "\""

        # Close the LINGUISTIC_TYPE node
        node += "/>\n"
        
        # Return the string representation of the XML node
        return node
    
    # Getter and setter methods
    def get_linguistic_type_id(self):
        return self.linguistic_type_id
    
    def get_ELAN_file(self):
        return self.ELAN_file
    
    def get_constraints(self):
        return self.constraints
    
    def get_graphic_references(self):
        return self.graphic_references
    
    def get_controlled_vocabulary_ref(self):
        return self.controlled_vocabulary_ref
    
    def get_external_ref(self):
        return self.external_ref
    
    def get_lexicon_ref(self):
        return self.lexicon_ref
    
    def set_linguistic_type_id(self, ID):
        self.linguistic_type_id = ID
    
    def set_ELAN_file(self, ELAN_file):
        self.ELAN_file = ELAN_file
    
    def set_constraints(self, constraints):        
        self.constraints = constraints
        
        if self.constraints is None:
            self.time_alignable = True
        elif self.constraints == "Time_Subdivision":
            self.time_alignable = True
        elif self.constraints == "Symbolic_Subdivision":
            self.time_alignable = False
        elif self.constraints == "Symbolic_Association":
            self.time_alignable = False
        elif self.constraints == "Included_In":
            self.time_alignable = True
        else:
            raise RuntimeError("Unknown constraint: " + self.constraints)
    
    def set_graphic_references(self, graphic_ref):        
        self.graphic_references = graphic_ref
    
    def set_controlled_vocabulary_ref(self, cv_ref):
        self.controlled_vocabulary_ref = cv_ref
    
    def set_external_ref(self, external_ref):
        self.external_ref = external_ref
    
    def set_lexicon_ref(self, lexicon_ref):
        self.lexicon_ref = lexicon_ref
        
    def set_time_alignable(self, time_alignable):
        if time_alignable is True:
            if self.constraints is not None and self.constraints != "Time_Subdivison" and self.constraints != "Included_In":
                raise RuntimeError("Constraint " + self.constraints + " is not time alignable.")
        
        elif time_alignable is False:
            if self.constraints is None or self.constraints == "Symbolic_Subdivision" or self.constraints == "Symbolic_Association":
                raise RuntimeError("Constraint " + self.constraints + " is time alignable.")
        
        self.time_alignable = time_alignable
    
    def is_time_alignable(self):
        if self.time_alignable is True:
            return True
        else:
            return False
    
    def has_time_alignable_flag(self):
        if self.time_alignable is not None:
            return True
        else:
            return False

    def has_time_constraints(self):
        if self.constraints is not None:
            return True
        else:
            return False
    
    def has_graphic_references_flag(self):
        if self.graphic_references is not None:
            return True
        else:
            return False
    
    def has_graphic_references(self):
        if self.graphic_references is True:
            return True
        else:
            return False
    
    def has_controlled_vocabulary_ref(self):
        if self.controlled_vocabulary_ref is not None:
            return True
        else:
            return False
    
    def has_external_ref(self):
        if self.external_ref is not None:
            return True
        else:
            return False
    
    def has_lexicon_ref(self):
        if self.lexicon_ref is not None:
            return True
        else:
            return False
    
    def has_constraints(self):
        if self.constraints is not None:
            return True
        else:
            return False
    
    # Useful hooks
    def __eq__(self, other):
        
        # Comparison with a type id as string
        if type(other) == "str":
            if self.linguistic_type_id == other:
                return True
            else:
                return False
        
        # Comparison with another ELANLinguisticType object
        elif type(other) == "ELANLinguisticType":
            if self.linguistic_type_id == other.linguistic_type_id and self.constraints == other.constraints and self.time_alignable == other.time_alignable:
                return True
            else:
                return False
        
        # Incompatible type
        else:
            return False
    
    def __ne__(self, other):
        if self == other:
            return False
        else:
            return True
            

# Class to model an ELAN linguistic constraint
class ELANConstraint:
    
    stereotype = None       # Required
    description = None      # Required
    
    # Constructor
    def __init__(self, stereotype, description):
        self.stereotype = stereotype
        self.description = description

    # Factory method to construct an ELANConstraint object
    # from a DOM xml node
    @classmethod
    def from_xml(cls, xml_node):
        
        # Make sure that the xml_node has the correct type
        if xml_node.tagName != "CONSTRAINT":
            raise RuntimeError("Cannot construct an ELANConstraint object from xml node of type " + xml_node.tagName)
        
        if xml_node.hasAttribute("STEREOTYPE"):
            stereotype = xml_node.getAttribute("STEREOTYPE")
        else:
            raise RuntimeError("CONSTRAINT is missing STEREOTYPE attribute.")

        if xml_node.hasAttribute("DESCRIPTION"):
            description = xml_node.getAttribute("DESCRIPTION")
        else:
            description = None

        # TODO: Maybe check for superfluous unknown attributes

        return cls(stereotype, description)

    # Method to produce an xml description from an ELANConstraint object
    def to_xml(self, indent="    "):

        # Construct a new xml node
        node = indent + "<CONSTRAINT"

        # Add STEREOTYPE
        node += " STEREOTYPE=\"" + escape(self.get_stereotype()) + "\""
        
        # Add DESCRIPTION attribute if there is one
        if self.has_description():
            
            node += " DESCRIPTION=\"" + escape(self.get_description()) + "\""

        # Close the CONSTRAINT node
        node += "/>\n"
        
        # Return the string representation of the XML node
        return node
        
    # Getter and setter methods
    def get_stereotype(self):
        return self.stereotype
    
    def get_description(self):
        return self.description
    
    def set_stereotype(self, stereotype):
        self.stereotype = stereotype
    
    def set_description(self, description):
        self.description = description

    def has_description(self):
        if self.description is not None:
            return True
        else:
            return False
    
    def is_time_alignable(self):
        if self.stereotype == "Time_Subdivision":
            return True
        elif self.stereotype == "Symbolic_Subdivision":
            return False
        elif self.stereotype == "Symbolic_Association":
            return False
        elif self.stereotype == "Included_In":
            return True
    
    def is_subdivision(self):
        if self.stereotype == "Time_Subdivision":
            return True
        elif self.stereotype == "Symbolic_Subdivision":
            return True
        elif self.stereotype == "Symbolic_Association":
            return False
        elif self.stereotype == "Included_In":
            return True
    
    def __eq__(self, other):
        if self.stereotype == other.stereotype:
            return True
        else:
            return False
    
    def __ne__(self, other):
        if self == other:
            return False
        else:
            return True
    
    def __hash__(self):
        return hash(self.stereotype)
    
    def __str__(self):
        return self.stereotype
    
    def __repr__(self):
        return self.stereotype
        

# Class to model a single controlled vocabulary entry
class ELANControlledVocabularyEntry:

    # Value
    value = None        # Required
    
    # Description
    description = None  # Optional
    
    # External reference (to ISOCat category)
    ext_ref = None      # Optional

    # Reference to controlled vocabulary containing the entry
    cv_ref = None       # Obligatory

    # Constructor
    def __init__(self, value, cv_ref, description=None, ext_ref=None):
        self.value = value
        self.cv_ref = cv_ref
        self.description = description
        self.ext_ref = ext_ref

    # Factory method to construct an ELANControlledVocabularyEntry object
    # from a DOM xml node
    @classmethod
    def from_xml(cls, xml_node, controlled_vocabulary):
        
        # Make sure that the xml_node has the correct type
        if xml_node.tagName != "CV_ENTRY":
            raise RuntimeError("Cannot construct an ELANControlledVocabularyEntry object from xml node of type " + xml_node.tagName)

        if xml_node.hasAttribute("DESCRIPTION"):
            description = xml_node.getAttribute("DESCRIPTION")
        else:
            description = None

        if xml_node.hasAttribute("EXT_REF"):
            external_ref = xml_node.getAttribute("EXT_REF")
        else:
            external_ref = None

        # Get the contents of the controlled vocabulary entry
        if xml_node.hasChildNodes():
            
            if xml_node.firstChild.nodeType == xml_node.TEXT_NODE:
                
                value = xml_node.firstChild.data
            
            else:
                
                value = ""
        
        else:
            
            value = ""

        # TODO: Maybe check for superfluous unknown attributes

        return cls(value, controlled_vocabulary, description, external_ref)

    # Method to produce an xml description from an ELANControlledVocabularyEntry object
    def to_xml(self, indent="    "):

        # Construct a new xml node
        node = 2 * indent + "<CV_ENTRY"
        
        # Add DESCRIPTION attribute if there is one
        if self.has_description():
            
            node += " DESCRIPTION=\"" + escape(self.get_description()) + "\""

        # Add EXT_REF attribute if there is one
        if self.has_ext_ref():
            
            node += " EXT_REF=\"" + escape(self.get_ext_ref()) + "\""
        
        # Close CV_ENTRY start tag
        node += ">"
        
        # Add the value
        node += escape(self.value)
        
        # Add end tag
        node += "</CV_ENTRY>\n"
        
        # Return the string representation of the XML node
        return node
    
    # Getter and setter methods
    def get_value(self):
        return self.value
    
    def get_cv_ref(self):
        return self.cv_ref
    
    def get_description(self):
        return self.description
    
    def get_ext_ref(self):
        return self.ext_ref
    
    def set_value(self, value):
        self.value = value
    
    def set_cv_ref(self, cv_ref):
        self.cv_ref = cv_ref
    
    def set_description(self, description):
        self.description = description
    
    def set_ext_ref(self, ext_ref):
        self.ext_ref = ext_ref
    
    def has_ext_ref(self):
        if self.ext_ref is not None:
            return True
        else:
            return False
    
    def has_description(self):
        if self.description is not None:
            return True
        else:
            return False
    
    def __eq__(self, other):
        
        # Compare value to string
        if isinstance(other, str):
            if self.value == other:
                return True
            else:
                return False
        
        # Compare two cv entries
        if isinstance(other, ELANControlledVocabularyEntry):
            if self.value == other.value:
                return True
            else:
                return False
        
        else:
            return False
    
    def __ne__(self, other):
        if self == other:
            return False
        else:
            return True
    
    def __lt__(self, other):
        if self.value < other.value:
            return True
        else:
            return False
    
    def __gt__(self, other):
        if self.value > other.value:
            return True
        else:
            return False
    
    def __le__(self, other):
        if self.value <= other.value:
            return True
        else:
            return False
    
    def __ge__(self, other):
        if self.value >= other.value:
            return True
        else:
            return False
    
    def __hash__(self):
        return hash(self.value)
    
    def __len__(self):
        return len(self.value)
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value + " " + str(self.description) + " " + str(self.ext_ref)


# Class to model a single controlled vocabulary
class ELANControlledVocabulary:
    
    # ID
    cv_id = None            # Required
    
    # Description
    description = None      # Optional
    
    # External reference
    ext_ref = None          # Optional
    
    # List of vocabulary entries
    cv_entries = []
    
    # Dictionary view of vocabulary entries
    cv_entries_dict = {}
    
    # Constructor
    def __init__(self, cv_id, description=None, ext_ref=None):
        self.cv_id = cv_id
        self.description = description
        self.ext_ref = ext_ref

    # Factory method to construct an ELANControlledVocabulary object
    # from a DOM xml node
    @classmethod
    def from_xml(cls, xml_node):
        
        # Make sure that the xml_node has the correct type
        if xml_node.tagName != "CONTROLLED_VOCABULARY":
            raise RuntimeError("Cannot construct an ELANControlledVocabulary object from xml node of type " + xml_node.tagName)
        
        if xml_node.hasAttribute("CV_ID"):
            cv_id = xml_node.getAttribute("CV_ID")
        else:
            raise RuntimeError("CONTROLLED_VOCABULARY is missing CV_ID attribute.")

        if xml_node.hasAttribute("DESCRIPTION"):
            description = xml_node.getAttribute("DESCRIPTION")
        else:
            description = None
        
        if xml_node.hasAttribute("EXT_REF"):
            external_ref = xml_node.getAttribute("EXT_REF")
        else:
            external_ref = None

        # TODO: Maybe check for superfluous unknown attributes

        # Create a new ELANControlledVocabulary object
        cv = cls(cv_id, description, external_ref)
        
        # Look for CV entries
        for child_node in xml_node.childNodes:

            # Ignore text nodes
            if child_node.nodeType == child_node.TEXT_NODE:
                continue

            # Make sure that the child node has the correct type
            if child_node.tagName != "CV_ENTRY":
                raise RuntimeError("Cannot construct an ELANControlledVocabularyEntry object from xml node of type " + xml_node.tagName)
            
            # Construct a new ELANControlledVocabularyEntry object
            cv_entry = ELANControlledVocabularyEntry.from_xml(child_node, cv)
            
            # Add CV entry to list of CV entries
            cv.add_cv_entry(cv_entry)

        return cv

    # Method to produce an xml description from an ELANControlledVocabulary object
    def to_xml(self, indent="    "):

        # Construct a new xml node
        node = indent + "<CONTROLLED_VOCABULARY"
        
        # Add CV_ID
        node += " CV_ID=\"" + escape(self.get_cv_id()) + "\""

        # Add DESCRIPTION attribute if there is one
        if self.has_description():
            
            node += " DESCRIPTION=\"" + escape(self.get_description()) + "\""

        # Add EXT_REF attribute if there is one
        if self.has_ext_ref():
            
            node += " EXT_REF=\"" + escape(self.get_ext_ref()) + "\""
        
        # Close CONTROLLED_VOCABULARY start tag
        node += ">\n"
        
        # Add controlled vocabulary entries
        for cv_entry in self:
            
            node += cv_entry.to_xml(indent=indent)
        
        # Add end tag
        node += indent + "</CONTROLLED_VOCABULARY>\n"
        
        # Return the string representation of the XML node
        return node
    
    # Getter and setter methods
    def get_cv_id(self):
        return self.cv_id
    
    def get_description(self):
        return self.description
    
    def get_ext_ref(self):
        return self.ext_ref
    
    def get_cv_entries(self):
        return self.cv_entries
    
    def get_cv_entries_dict(self):
        return self.cv_entries_dict
    
    def set_cv_id(self, cv_id):
        self.cv_id = cv_id
    
    def set_description(self, description):
        self.description = description
    
    def set_ext_ref(self, ext_ref):
        self.ext_ref = ext_ref
    
    def has_ext_ref(self):
        if self.ext_ref is not None:
            return True
        else:
            return False
    
    def has_description(self):
        if self.description is not None:
            return True
        else:
            return False
    
    def is_empty(self):
        if len(self) == 0:
            return True
        else:
            return False
    
    def add_cv_entry(self, cv_entry):
        
        # Check whether the controlled vocabulary
        # is stored in an external file
        if self.ext_ref is None:            
            if not isinstance(cv_entry, ELANControlledVocabularyEntry):
                raise TypeError("Controlled vocabulary entries must be of type ELANControlledVocabularyEntry.")
            
            # Only add new, non-redundant entries
            if cv_entry.get_value() not in self.cv_entries_dict:
                self.cv_entries.append(cv_entry)
                self.cv_entries_dict[cv_entry.get_value()] = cv_entry

        else:
            raise RuntimeError("Cannot add entries to a controlled vocabulary pointing to an external reference.")
    
    # Search for and return a particular cv entry
    def get_cv_entry_by_value(self, value):
        if value in self.cv_entries_dict:
            return self.cv_entries_dict[value]
        else:
            return None
    
    def __eq__(self, other):
        
        # If compared to a string, assume
        # that the string represents the cv_id
        if type(other) == "str":
            if self.cv_id == other:
                return True
            else:
                return False
            
        # If compared to another ELANControlledVocabulary object,
        # assume that the cv_id and the optional external reference
        # have to be the same
        elif type(other) == "ELANControlledVocabulary":
            if self.cv_id == other.cv_id and self.ext_ref == other.ext_ref:
                return True
            else:
                return False
        
        else:
            return False
    
    def __ne__(self, other):
        if self == other:
            return True
        else:
            return False
    
    def __hash__(self):
        return hash(self.cv_id + " " + self.ext_ref)
    
    def __str__(self):
        return self.cv_id
    
    def __repr__(self):
        return self.cv_id + " " + str(self.ext_ref)
    
    def __iter__(self):
        return iter(self.cv_entries)
    
    def __len__(self):
        return len(self.cv_entries)


# Class to model a single external reference
class ELANExternalReference:
    
    # ID
    ext_ref_id = None       # Required
    
    # Type of external reference
    ext_ref_type = None     # Required
    
    # Value of the external reference    # Required
    value = None
    
    # Constructor
    def __init__(self, ext_ref_id, ext_ref_type, value):
        self.ext_ref_id = ext_ref_id
        
        # Check that a correct type is used
        if ext_ref_type not in ["iso12620", "ecv", "cve_id", "lexen_id", "resource_url"]:
            raise RuntimeError("Unknown type of external reference: " + str(ext_ref_type))
        
        self.ext_ref_type = ext_ref_type
        self.value = value

    # Factory method to construct an ELANExternalReference object
    # from a DOM xml node
    @classmethod
    def from_xml(cls, xml_node):
        
        # Make sure that the xml_node has the correct type
        if xml_node.tagName != "EXTERNAL_REF":
            raise RuntimeError("Cannot construct an ELANExternalReference object from xml node of type " + xml_node.tagName)
        
        if xml_node.hasAttribute("EXT_REF_ID"):
            external_ref_id = xml_node.getAttribute("EXT_REF_ID")
        else:
            raise RuntimeError("EXTERNAL_REF is missing EXT_REF_ID attribute.")

        if xml_node.hasAttribute("TYPE"):
            external_ref_type = xml_node.getAttribute("TYPE")
        else:
            raise RuntimeError("EXTERNAL_REF is missing TYPE attribute.")
        
        # Get the contents of external reference
        if xml_node.hasChildNodes():
            
            if xml_node.firstChild.nodeType == xml_node.TEXT_NODE:
                
                external_ref_value = xml_node.firstChild.data
            
            else:
                
                raise RuntimeError("EXTERNAL_REF is empty.")
        
        else:
            
            raise RuntimeError("EXTERNAL_REF is empty.")

        # TODO: Maybe check for superfluous unknown attributes

        return cls(external_ref_id, external_ref_type, external_ref_value)

    # Method to produce an xml description from an ELANExternalReference object
    def to_xml(self, indent="    "):

        # Construct a new xml node
        node = indent + "<EXTERNAL_REF"
        
        # Add EXT_REF_ID
        node += " EXT_REF_ID=\"" + escape(self.get_ext_ref_id()) + "\""

        # Add TYPE
        node += " TYPE=\"" + escape(self.get_type()) + "\""
                
        # Close EXTERNAL_REF start tag
        node += ">\n"
        
        # Add value
        node += escape(self.get_value())
        
        # Add end tag
        node += "</EXTERNAL_REF>\n"
        
        # Return the string representation of the XML node
        return node

    # Getter and setter methods
    def get_id(self):
        return self.ext_ref_id
    
    def get_type(self):
        return self.ext_ref_type
    
    def get_value(self):
        return self.value
    
    def set_id(self, ext_ref_id):
        self.ext_ref_id = ext_ref_id
    
    def set_type(self, ext_ref_type):
        self.ext_ref_type = ext_ref_type
    
    def set_value(self, value):
        self.value = value
    
    def refers_to_isocat(self):
        if self.ext_ref_type == "iso12620":
            return True
        else:
            return False
    
    def refers_to_external_cv(self):
        if self.ext_ref_type == "ecv":
            return True
        else:
            return False
    
    def refers_to_external_cv_entry(self):
        if self.ext_ref_type == "cve_id":
            return True
        else:
            return False
    
    def refers_to_lexeme(self):
        if self.ext_ref_type == "lexen_id":
            return True
        else:
            return False
    
    def refers_to_url(self):
        if self.ext_ref_type == "resource_url":
            return True
        else:
            return False
    
    def __eq__(self, other):
        if self.ext_ref_id == other.ext_ref_id and self.ext_ref_type == other.ext_ref_type and self.value == other.value:
            return True
        else:
            return False
    
    def __ne__(self, other):
        if self == other:
            return False
        else:
            return True
    

# Class to model an ELAN locale
class ELANLocale:
    
    # Language code
    language_code = None    # Required
    
    # Country code
    country_code = None     # Optional
    
    # Variant
    variant = None          # Optional
    
    # Constructor
    def __init__(self, language_code, country_code=None, variant=None):
        self.language_code = language_code
        self.country_code = country_code
        self.variant = variant

    # Factory method to construct an ELANLocale object
    # from a DOM xml node
    @classmethod
    def from_xml(cls, xml_node):
        
        # Make sure that the xml_node has the correct type
        if xml_node.tagName != "LOCALE":
            raise RuntimeError("Cannot construct an ELANLocale object from xml node of type " + xml_node.tagName)
        
        if xml_node.hasAttribute("LANGUAGE_CODE"):
            language_code = xml_node.getAttribute("LANGUAGE_CODE")
        else:
            raise RuntimeError("LOCALE is missing LANGUAGE_CODE attribute.")

        if xml_node.hasAttribute("COUNTRY_CODE"):
            country_code = xml_node.getAttribute("COUNTRY_CODE")
        else:
            country_code = None

        if xml_node.hasAttribute("VARIANT"):
            variant = xml_node.getAttribute("VARIANT")
        else:
            variant = None

        # TODO: Maybe check for superfluous unknown attributes

        return cls(language_code, country_code, variant)

    # Method to produce an xml description from an ELANLocale object
    def to_xml(self, indent="    "):

        # Construct a new xml node
        node = indent + "<LOCALE"
        
        # Add LANGUAGE_CODE
        node += " LANGUAGE_CODE=\"" + escape(self.get_language_code()) + "\""

        # Add COUNTRY_CODE if there is one
        if self.has_country_code():
            node += " COUNTRY_CODE=\"" + escape(self.get_country_code()) + "\""

        # Add VARIANT if there is one
        if self.has_variant():
            node += " VARIANT=\"" + escape(self.get_variant()) + "\""
                
        # Close LOCALE node
        node += "/>\n"
        
        # Return the string representation of the XML node
        return node
    
    # Getter and setter methods
    def get_language_code(self):
        return self.language_code
    
    def get_country_code(self):
        return self.country_code
    
    def get_variant(self):
        return self.variant
    
    def set_language_code(self, language_code):
        self.language_code = language_code
    
    def set_country_code(self, country_code):
        self.country_code = country_code
    
    def set_variant(self, variant):
        self.variant = variant
    
    def has_country_code(self):
        if self.country_code is not None:
            return True
        else:
            return False
    
    def has_variant(self):
        if self.variant is not None:
            return True
        else:
            return False
    
    def __eq__(self, other):    
        if self.language_code == other.language_code and self.country_code == other.country_code and self.variant == other.variant:
            return True
        else:
            return False
    
    def __ne__(self, other):
        if self == other:
            return False
        else:
            return True
    
    def __hash__(self):
        return hash(self.language_code + " " + str(self.country_code) + " " + str(self.variant))


# Class to model an ELAN lexicon reference
class ELANLexiconReference:
    
    # Lexicon reference ID
    lex_ref_id = None       # Required
    
    # Name
    lex_ref_name = None     # Required
    
    # Type
    lex_ref_type = None     # Required
    
    # URL
    url = None              # Required
    
    # Lexicon ID
    lexicon_id = None       # Required
    
    # Lexicon name
    lexicon_name = None     # Required
    
    # Data category id
    datcat_id = None        # Optional
    
    # Data category name
    datcat_name = None      # Optional
    
    # Constructor
    def __init__(self, lex_ref_id, lex_ref_name, lex_ref_type, url, lexicon_id, lexicon_name, datcat_id=None, datcat_name=None):
        self.lex_ref_id = lex_ref_id
        self.lex_ref_name = lex_ref_name
        self.lex_ref_type = lex_ref_type
        self.url = url
        self.lexicon_id = lexicon_id
        self.lexicon_name = lexicon_name
        self.datcat_id = datcat_id
        self.datcat_name = datcat_name

    # Factory method to construct an ELANLexiconReference object
    # from a DOM xml node
    @classmethod
    def from_xml(cls, xml_node):
        
        # Make sure that the xml_node has the correct type
        if xml_node.tagName != "LEXICON_REF":
            raise RuntimeError("Cannot construct an ELANLexiconReference object from xml node of type " + xml_node.tagName)
        
        if xml_node.hasAttribute("LEX_REF_ID"):
            lexicon_ref_id = xml_node.getAttribute("LEX_REF_ID")
        else:
            raise RuntimeError("LEXICON_REF is missing LEX_REF_ID attribute.")

        if xml_node.hasAttribute("NAME"):
            name = xml_node.getAttribute("NAME")
        else:
            raise RuntimeError("LEXICON_REF is missing NAME attribute.")

        if xml_node.hasAttribute("TYPE"):
            lexicon_ref_type = xml_node.getAttribute("TYPE")
        else:
            raise RuntimeError("LEXICON_REF is missing TYPE attribute.")

        if xml_node.hasAttribute("URL"):
            url = xml_node.getAttribute("URL")
        else:
            raise RuntimeError("LEXICON_REF is missing URL attribute.")

        if xml_node.hasAttribute("LEXICON_ID"):
            lexicon_id = xml_node.getAttribute("LEXICON_ID")
        else:
            raise RuntimeError("LEXICON_REF is missing LEXICON_ID attribute.")

        if xml_node.hasAttribute("LEXICON_NAME"):
            lexicon_name = xml_node.getAttribute("LEXINCON_NAME")
        else:
            raise RuntimeError("LEXICON_REF is missing LEXICON_NAME attribute.")

        if xml_node.hasAttribute("DATCAT_ID"):
            datcat_id = xml_node.getAttribute("DATCAT_ID")
        else:
            datcat_id = None

        if xml_node.hasAttribute("DATCAT_NAME"):
            datcat_name = xml_node.getAttribute("DATCAT_NAME")
        else:
            datcat_name = None

        # TODO: Maybe check for superfluous unknown attributes

        return cls(lexicon_ref_id, name, lexicon_ref_type, url, lexicon_id, lexicon_name, datcat_id, datcat_name)

    # Method to produce an xml description from an ELANLexiconReference object
    def to_xml(self, indent="    "):

        # Construct a new xml node
        node = indent + "<LEXICON_REF"
        
        # Add LEXICON_REF_ID
        node += " LEXICON_REF_ID=\"" + escape(self.get_id()) + "\""

        # Add NAME
        node += " NAME=\"" + escape(self.get_name()) + "\""

        # Add TYPE
        node += " TYPE=\"" + escape(self.get_type()) + "\""

        # Add URL
        node += " URL=\"" + escape(self.get_url()) + "\""

        # Add LEXICON_ID
        node += " LEXICON_ID=\"" + escape(self.get_lexicon_id()) + "\""

        # Add LEXICON_NAME
        node += " LEXICON_NAME=\"" + escape(self.get_lexicon_name()) + "\""

        # Add DATCAT_ID if there is one
        if self.has_datcat_id():
            node += " DATCAT_ID=\"" + escape(self.get_datcat_id()) + "\""

        # Add DATCAT_NAME if there is one
        if self.has_datcat_name():
            node += " DATCAT_NAME=\"" + escape(self.get_datcat_name()) + "\""

        # Close LEXICON_REF node
        node += "/>\n"
        
        # Return the string representation of the XML node
        return node
    
    # Getter and setter methods
    def get_id(self):
        return self.lex_ref_id
    
    def get_name(self):
        return self.lex_ref_name
    
    def get_type(self):
        return self.lex_ref_type
    
    def get_url(self):
        return self.url
    
    def get_lexicon_id(self):
        return self.lexicon_id
    
    def get_lexicon_name(self):
        return self.lexicon_name
    
    def get_datcat_id(self):
        return self.datcat_id
    
    def get_datcat_name(self):
        return self.datcat_name
    
    def set_id(self, lex_ref_id):
        self.lex_ref_id = lex_ref_id
    
    def set_name(self, lex_ref_name):
        self.lex_ref_name = lex_ref_name
    
    def set_type(self, lex_ref_type):
        self.lex_ref_type
    
    def set_lexicon_id(self, lexicon_id):
        self.lexicon_id = lexicon_id
    
    def set_lexicon_name(self, lexicon_name):
        self.lexicon_name = lexicon_name
    
    def set_datcat_id(self, datcat_id):
        self.datcat_id = datcat_id
    
    def set_datcat_name(self, datcat_name):
        self.datcat_name = datcat_name
    
    def has_datcat_id(self):
        if self.datcat_id is not None:
            return True
        else:
            return False
    
    def has_datcat_name(self):
        if self.datcat_name is not None:
            return True
        else:
            return False
    
    def __str__(self):
        return self.lex_ref_id

    
# Class to model a complete ELAN file
class ELANFile:
    
    # File name
    URL = None
    
    # Parsed xml tree of the file
    xml_tree = None
    
    # Basic metadata
    author = None       # required
    date = None         # required
    format = None       # optional
    version = None      # required
    
    # Time units used (defaults to milliseconds)
    time_units = None
    
    # List of linked media files
    media_files = []
    
    # List of other linked files
    linked_files = []
    
    # Key-value pairs
    properties = {}
    
    # Time order (containing time slots as anchors for annotations)
    time_order = None
    
    # List of tiers
    tiers = []
    
    # List of linguistic types
    linguistic_types = []
    
    # List of constraints
    constraints = []
    
    # List of controlled vocabularies
    controlled_vocabularies = []
    
    # Locales
    locales = []
    
    # List of references to lexicons
    lexicon_references = []
    
    # List of external references
    external_references = []

    # Dictionary views on relevant parts of the ELAN document
    # Dictionary view on all media files
    media_files_dict = {}

    # Dictionary view on all linked files
    linked_files_dict = {}
    
    # Dictionary view on all time slots
    time_slots_dict = {}
    
    # Dictionary view on all tiers
    tiers_dict = {}
    
    # Dictionary view on all annotations contained in all tiers
    annotations_dict = {}
    
    # Dictionary view on all linguistic types
    linguistic_types_dict = {}
    
    # Dictionary view on all constraints
    constraints_dict = {}
    
    # Dictionary view on all controlled vocabularies
    controlled_vocabularies_dict = {}
    
    # Dictionary view on all external references
    external_references_dict = {}

    # Dictionary view on all lexicon references
    lexicon_references_dict = {}

    # Constructor
    def __init__(self):
        
        pass

    @classmethod
    def read_elan_file(cls, file_name):
        xml_tree = dom.parse(file_name)
        return ELANFile.parse_xml(xml_tree, file_name)

    # Method to convert an xml tree into the ELANFile object and its components
    @classmethod
    def parse_xml(cls, xml_tree, file_name):
        
        # TODO: (Re)initialize values in order to make sure
        # that no contamination between different ELANFile objects occurs
        
        # Create a new ELANFile object
        elan_file = cls()
        elan_file.xml_tree = xml_tree
        elan_file.url = file_name
        
        # Basic metadata
        elan_file.author = None
        elan_file.date = None
        elan_file.format = None
        elan_file.version = None

        # Time units used (defaults to milliseconds)
        elan_file.time_units = None
    
        # List of linked media files
        elan_file.media_files = []
    
        # List of other linked files
        elan_file.linked_files = []
    
        # Key-value pairs
        elan_file.properties = {}
    
        # Time order (containing time slots as anchors for annotations)
        elan_file.time_order = None
    
        # List of tiers
        elan_file.tiers = []
    
        # List of linguistic types
        elan_file.linguistic_types = []
    
        # List of constraints
        elan_file.constraints = []
    
        # List of controlled vocabularies
        elan_file.controlled_vocabularies = []
    
        # Locales
        elan_file.locales = []
    
        # List of references to lexicons
        elan_file.lexicon_references = []
    
        # List of external references
        elan_file.external_references = []

        # Dictionary views on relevant parts of the ELAN document
        # Dictionary view on all media files
        elan_file.media_files_dict = {}

        # Dictionary view on all linked files
        elan_file.linked_files_dict = {}
    
        # Dictionary view on all time slots
        elan_file.time_slots_dict = {}
    
        # Dictionary view on all tiers
        elan_file.tiers_dict = {}
    
        # Dictionary view on all annotations contained in all tiers
        elan_file.annotations_dict = {}
    
        # Dictionary view on all linguistic types
        elan_file.linguistic_types_dict = {}
    
        # Dictionary view on all constraints
        elan_file.constraints_dict = {}
    
        # Dictionary view on all controlled vocabularies
        elan_file.controlled_vocabularies_dict = {}
    
        # Dictionary view on all external references
        elan_file.external_references_dict = {}

        # Dictionary view on all lexicon references
        elan_file.lexicon_references_dict = {}

        # Only look at the surrounding ANNOTATION_DOCUMENT element        
        xml_tree = xml_tree.firstChild
        
        # Make sure the document node has the right type
        if xml_tree.nodeName == "ANNOTATION_DOCUMENT":
            
            # Extract meta data from outer ANNOTATION_DOCUMENT node
            # Extract information about the author
            if xml_tree.hasAttribute("AUTHOR"):
                elan_file.author = xml_tree.getAttribute("AUTHOR")
            
            # Extract information about the date
            if xml_tree.hasAttribute("DATE"):
                elan_file.date = xml_tree.getAttribute("DATE")

            # Extract information about the format
            if xml_tree.hasAttribute("FORMAT"):
                elan_file.format = xml_tree.getAttribute("FORMAT")

            # Extract information about the version
            if xml_tree.hasAttribute("VERSION"):
                elan_file.version = xml_tree.getAttribute("VERSION")

            # Process child nodes of document node
            for child_node in xml_tree.childNodes:
                
                # Skip non-element nodes
                if child_node.nodeType != child_node.ELEMENT_NODE:
                    continue
                
                # Determine type of node
                if child_node.tagName == "HEADER":
                    
                    # Extract information from the header
                    # Deprecated MEDIA_FILE attribute
                    if child_node.hasAttribute("MEDIA_FILE"):
                        elan_file.media_file = child_node.getAttribute("MEDIA_FILE")

                    # Largely redundant TIME_UNITS attribute (should always be milliseconds)
                    if child_node.hasAttribute("TIME_UNITS"):
                        elan_file.media_file = child_node.getAttribute("TIME_UNITS")
                    
                    # Assume default value
                    else:
                        elan_file.time_units = "milliseconds"
                    
                    # Process parts of the header
                    for header_child_node in child_node.childNodes:
                        
                        # Skip non-element nodes
                        if header_child_node.nodeType != header_child_node.ELEMENT_NODE:
                            continue
                        
                        if header_child_node.tagName == "MEDIA_DESCRIPTOR":
                            
                            # Construct a new ELANMediaDescriptor object
                            media_descriptor = ELANMediaDescriptor.from_xml(header_child_node)
                            
                            # Append the ELANMediaDescriptor object to the list of media files
                            elan_file.media_files.append(media_descriptor)
                            
                            # Also add it to the hash view on media files
                            elan_file.media_files_dict[media_descriptor.get_media_url()] = media_descriptor
                        
                        elif header_child_node.tagName == "LINKED_FILE_DESCRIPTOR":
                            
                            # Construct a new ELANLinkedFileDescriptor
                            linked_file_descriptor = ELANLinkedFileDescriptor.from_xml(header_child_node)
                            
                            # Append the ELANLinkedFileDescriptor object to the list of linked files
                            elan_file.linked_files.append(linked_file_descriptor)
                            
                            # Also add it to the hash view on linked files
                            elan_file.linked_files_dict[linked_file_descriptor.get_link_url()] = linked_file_descriptor
                        
                        elif header_child_node.tagName == "PROPERTY":
                            
                            # Name of the property is in the NAME attribute
                            if header_child_node.hasAttribute("NAME"):
                                name = header_child_node.getAttribute("NAME")
                            else:
                                raise RuntimeError("PROPERTY element is missing NAME attribute.")

                            # Get the value of the property
                            if header_child_node.hasChildNodes():
                                
                                if header_child_node.firstChild.nodeType == header_child_node.TEXT_NODE:

                                    value = header_child_node.firstChild.data

                                else:
                                    
                                    raise RuntimeError("PROPERTY is empty.")

                            else:

                                raise RuntimeError("PROPERTY is empty.")
                            
                            # Add property to properties hash
                            elan_file.properties[name] = value
                            
                        else:
                            raise RuntimeError("Unknown ELAN header entry: " + header_child_node.tagName)
                
                elif child_node.tagName == "TIME_ORDER":
                    
                    # Construct a new time order from the xml_node
                    elan_file.time_order = ELANTimeOrder.from_xml(child_node, elan_file)
                    
                    # Also construct a dictionary view on the time slots
                    # in the time order
                    for time_slot in elan_file.time_order:
                        
                        # Add current time slot to dictionary of time slots
                        elan_file.time_slots_dict[time_slot.get_id()] = time_slot                    
                
                elif child_node.tagName == "TIER":
                    
                    # Construct a new tier from the xml node
                    tier = ELANTier.from_xml(child_node, elan_file)
                    
                    # Add tier to the list of tiers
                    elan_file.tiers.append(tier)
                    
                    # Add tier to the dictionary view on tiers
                    elan_file.tiers_dict[tier.get_tier_id()] = tier
                    
                    # Go through all annotations on the tier
                    # and add them to the dictionary view on annotations
                    for annotation in tier:
                        
                        # Add annotation to the dictionary view on annotations
                        elan_file.annotations_dict[annotation.get_annotation_id()] = annotation
                
                elif child_node.tagName == "LINGUISTIC_TYPE":
                    
                    # Construct a new linguistic type from the xml node
                    linguistic_type = ELANLinguisticType.from_xml(child_node, elan_file)
                    
                    # Add linguistic type to the list of linguistic types
                    elan_file.linguistic_types.append(linguistic_type)
                    
                    # Add linguistic type to the dictionary view on linguistic types
                    elan_file.linguistic_types_dict[linguistic_type.get_linguistic_type_id()] = linguistic_type
                                    
                elif child_node.tagName == "CONSTRAINT":
                    
                    # Construct a new constraint from the xml node
                    constraint = ELANConstraint.from_xml(child_node)
                    
                    # Add constraint to the list of constraints
                    elan_file.constraints.append(constraint)
                    
                    # Add constraint to the dictionary view on constraints
                    elan_file.constraints_dict[constraint.get_stereotype()] = constraint
                
                elif child_node.tagName == "CONTROLLED_VOCABULARY":
                    
                    # Construct a new controlled vocabulary
                    controlled_vocabulary = ELANControlledVocabulary.from_xml(child_node)
                    
                    # Add controlled vocabulary to the list of controlled vocabularies
                    elan_file.controlled_vocabularies.append(controlled_vocabulary)
                    
                    # Add controlled vocabulary to the dictionary view on controlled vocabularies
                    elan_file.controlled_vocabularies_dict[controlled_vocabulary.get_cv_id()] = controlled_vocabulary

                elif child_node.tagName == "EXTERNAL_REF":
                    
                    # Construct a new external reference from xml node
                    external_ref = ELANExternalReference.from_xml(child_node)
                    
                    # Add external reference to the list of external references
                    elan_file.external_references.append(external_ref)
                    
                    # Add external reference to the dictionary view on external references
                    elan_file.external_references_dict[external_ref.get_id()] = external_ref
                
                elif child_node.tagName == "LOCALE":
                    
                    # Construct a new locale from the xml node
                    locale = ELANLocale.from_xml(child_node)
                    
                    # Add the locale to the list of locales
                    elan_file.locales.append(locale)
                
                elif child_node.tagName == "LEXICON_REF":
                    
                    # Construct a new lexicon reference
                    lexicon_ref = ELANLexiconReference.from_xml(child_node)
                    
                    # Add lexicon reference to the list of lexicon references
                    elan_file.lexicon_references.append(lexicon_ref)
                    
                    # Add lexicon reference to the dictionary view on lexicon references
                    elan_file.lexicon_references_dict[lexicon_ref.get_id()] = lexicon_ref
                
                else:
                    raise RuntimeError("Unknown XML node: " + child_node.tagName)
        
        else:
            raise RuntimeError("XML document does not have the correct type ANNOTATION_DOCUMENT.")

        # Return the created ELANFile object
        return elan_file

#    # Method to convert an xml tree into the ELANFile object and its components
#    def parse_xml(self, xml_tree):
#        
#        # (Re)initialize values in order to make sure
#        # that no contamination between different ELANFile objects occurs
#        
#        # Basic metadata
#        self.author = None
#        self.date = None
#        self.format = None
#        self.version = None
#
#        # Time units used (defaults to milliseconds)
#        self.time_units = None
#    
#        # List of linked media files
#        self.media_files = []
#    
#        # List of other linked files
#        self.linked_files = []
#    
#        # Key-value pairs
#        self.properties = {}
#    
#        # Time order (containing time slots as anchors for annotations)
#        self.time_order = None
#    
#        # List of tiers
#        self.tiers = []
#    
#        # List of linguistic types
#        self.linguistic_types = []
#    
#        # List of constraints
#        self.constraints = []
#    
#        # List of controlled vocabularies
#        self.controlled_vocabularies = []
#    
#        # Locales
#        self.locales = []
#    
#        # List of references to lexicons
#        self.lexicon_references = []
#    
#        # List of external references
#        self.external_references = []
#
#        # Dictionary views on relevant parts of the ELAN document
#        # Dictionary view on all media files
#        self.media_files_dict = {}
#
#        # Dictionary view on all linked files
#        self.linked_files_dict = {}
#    
#        # Dictionary view on all time slots
#        self.time_slots_dict = {}
#    
#        # Dictionary view on all tiers
#        self.tiers_dict = {}
#    
#        # Dictionary view on all annotations contained in all tiers
#        self.annotations_dict = {}
#    
#        # Dictionary view on all linguistic types
#        self.linguistic_types_dict = {}
#    
#        # Dictionary view on all constraints
#        self.constraints_dict = {}
#    
#        # Dictionary view on all controlled vocabularies
#        self.controlled_vocabularies_dict = {}
#    
#        # Dictionary view on all external references
#        self.external_references_dict = {}
#
#        # Dictionary view on all lexicon references
#        self.lexicon_references_dict = {}
#
#        # Only look at the surrounding ANNOTATION_DOCUMENT element        
#        xml_tree = xml_tree.firstChild
#        
#        # Make sure the document node has the right type
#        if xml_tree.nodeName == "ANNOTATION_DOCUMENT":
#            
#            # Extract meta data from outer ANNOTATION_DOCUMENT node
#            # Extract information about the author
#            if xml_tree.hasAttribute("AUTHOR"):
#                self.author = xml_tree.getAttribute("AUTHOR")
#            
#            # Extract information about the date
#            if xml_tree.hasAttribute("DATE"):
#                self.date = xml_tree.getAttribute("DATE")
#
#            # Extract information about the format
#            if xml_tree.hasAttribute("FORMAT"):
#                self.format = xml_tree.getAttribute("FORMAT")
#
#            # Extract information about the version
#            if xml_tree.hasAttribute("VERSION"):
#                self.version = xml_tree.getAttribute("VERSION")
#
#            # Process child nodes of document node
#            for child_node in xml_tree.childNodes:
#                
#                # Skip non-element nodes
#                if child_node.nodeType != child_node.ELEMENT_NODE:
#                    continue
#                
#                # Determine type of node
#                if child_node.tagName == "HEADER":
#                    
#                    # Extract information from the header
#                    # Deprecated MEDIA_FILE attribute
#                    if child_node.hasAttribute("MEDIA_FILE"):
#                        self.media_file = child_node.getAttribute("MEDIA_FILE")
#
#                    # Largely redundant TIME_UNITS attribute (should always be milliseconds)
#                    if child_node.hasAttribute("TIME_UNITS"):
#                        self.media_file = child_node.getAttribute("TIME_UNITS")
#                    
#                    # Assume default value
#                    else:
#                        self.time_units = "milliseconds"
#                    
#                    # Process parts of the header
#                    for header_child_node in child_node.childNodes:
#                        
#                        # Skip non-element nodes
#                        if header_child_node.nodeType != header_child_node.ELEMENT_NODE:
#                            continue
#                        
#                        if header_child_node.tagName == "MEDIA_DESCRIPTOR":
#                            
#                            # Construct a new ELANMediaDescriptor object
#                            media_descriptor = ELANMediaDescriptor.from_xml(header_child_node)
#                            
#                            # Append the ELANMediaDescriptor object to the list of media files
#                            self.media_files.append(media_descriptor)
#                            
#                            # Also add it to the hash view on media files
#                            self.media_files_dict[media_descriptor.get_media_url()] = media_descriptor
#                        
#                        elif header_child_node.tagName == "LINKED_FILE_DESCRIPTOR":
#                            
#                            # Construct a new ELANLinkedFileDescriptor
#                            linked_file_descriptor = ELANLinkedFileDescriptor.from_xml(header_child_node)
#                            
#                            # Append the ELANLinkedFileDescriptor object to the list of linked files
#                            self.linked_files.append(linked_file_descriptor)
#                            
#                            # Also add it to the hash view on linked files
#                            self.linked_files_dict[linked_file_descriptor.get_link_url()] = linked_file_descriptor
#                        
#                        elif header_child_node.tagName == "PROPERTY":
#                            
#                            # Name of the property is in the NAME attribute
#                            if header_child_node.hasAttribute("NAME"):
#                                name = header_child_node.getAttribute("NAME")
#                            else:
#                                raise RuntimeError("PROPERTY element is missing NAME attribute.")
#
#                            # Get the value of the property
#                            if header_child_node.hasChildNodes():
#                                
#                                if header_child_node.firstChild.nodeType == header_child_node.TEXT_NODE:
#
#                                    value = header_child_node.firstChild.data
#
#                                else:
#                                    
#                                    raise RuntimeError("PROPERTY is empty.")
#
#                            else:
#
#                                raise RuntimeError("PROPERTY is empty.")
#                            
#                            # Add property to properties hash
#                            self.properties[name] = value
#                            
#                        else:
#                            raise RuntimeError("Unknown ELAN header entry: " + header_child_node.tagName)
#                
#                elif child_node.tagName == "TIME_ORDER":
#                    
#                    # Construct a new time order from the xml_node
#                    self.time_order = ELANTimeOrder.from_xml(child_node, self)
#                    
#                    # Also construct a dictionary view on the time slots
#                    # in the time order
#                    for time_slot in self.time_order:
#                        
#                        # Add current time slot to dictionary of time slots
#                        self.time_slots_dict[time_slot.get_id()] = time_slot                    
#                
#                elif child_node.tagName == "TIER":
#                    
#                    # Construct a new tier from the xml node
#                    tier = ELANTier.from_xml(child_node, self)
#                    
#                    # Add tier to the list of tiers
#                    self.tiers.append(tier)
#                    
#                    # Add tier to the dictionary view on tiers
#                    self.tiers_dict[tier.get_tier_id()] = tier
#                    
#                    # Go through all annotations on the tier
#                    # and add them to the dictionary view on annotations
#                    for annotation in tier:
#                        
#                        # Add annotation to the dictionary view on annotations
#                        self.annotations_dict[annotation.get_annotation_id()] = annotation
#                
#                elif child_node.tagName == "LINGUISTIC_TYPE":
#                    
#                    # Construct a new linguistic type from the xml node
#                    linguistic_type = ELANLinguisticType.from_xml(child_node, self)
#                    
#                    # Add linguistic type to the list of linguistic types
#                    self.linguistic_types.append(linguistic_type)
#                    
#                    # Add linguistic type to the dictionary view on linguistic types
#                    self.linguistic_types_dict[linguistic_type.get_linguistic_type_id()] = linguistic_type
#                                    
#                elif child_node.tagName == "CONSTRAINT":
#                    
#                    # Construct a new constraint from the xml node
#                    constraint = ELANConstraint.from_xml(child_node)
#                    
#                    # Add constraint to the list of constraints
#                    self.constraints.append(constraint)
#                    
#                    # Add constraint to the dictionary view on constraints
#                    self.constraints_dict[constraint.get_stereotype()] = constraint
#                
#                elif child_node.tagName == "CONTROLLED_VOCABULARY":
#                    
#                    # Construct a new controlled vocabulary
#                    controlled_vocabulary = ELANControlledVocabulary.from_xml(child_node)
#                    
#                    # Add controlled vocabulary to the list of controlled vocabularies
#                    self.controlled_vocabularies.append(controlled_vocabulary)
#                    
#                    # Add controlled vocabulary to the dictionary view on controlled vocabularies
#                    self.controlled_vocabularies_dict[controlled_vocabulary.get_cv_id()] = controlled_vocabulary
#
#                elif child_node.tagName == "EXTERNAL_REF":
#                    
#                    # Construct a new external reference from xml node
#                    external_ref = ELANExternalReference.from_xml(child_node)
#                    
#                    # Add external reference to the list of external references
#                    self.external_references.append(external_ref)
#                    
#                    # Add external reference to the dictionary view on external references
#                    self.external_references_dict[external_ref.get_id()] = external_ref
#                
#                elif child_node.tagName == "LOCALE":
#                    
#                    # Construct a new locale from the xml node
#                    locale = ELANLocale.from_xml(child_node)
#                    
#                    # Add the locale to the list of locales
#                    self.locales.append(locale)
#                
#                elif child_node.tagName == "LEXICON_REF":
#                    
#                    # Construct a new lexicon reference
#                    lexicon_ref = ELANLexiconReference.from_xml(child_node)
#                    
#                    # Add lexicon reference to the list of lexicon references
#                    self.lexicon_references.append(lexicon_ref)
#                    
#                    # Add lexicon reference to the dictionary view on lexicon references
#                    self.lexicon_references_dict[lexicon_ref.get_id()] = lexicon_ref
#                
#                else:
#                    raise RuntimeError("Unknown XML node: " + child_node.tagName)
#        
#        else:
#            raise RuntimeError("XML document does not have the correct type ANNOTATION_DOCUMENT.")

    # Method to produce an xml description from an ELANFile object
    def to_xml(self, indent="    "):

        # Construct a new xml node
        node = ""
        
        # Add XML header
        node += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        
        # Add root element
        node += "<ANNOTATION_DOCUMENT"
        
        # Add DATE
        node += " DATE=\"" + escape(self.get_date()) + "\""
        
        # Add AUTHOR
        node += " AUTHOR=\"" + escape(self.get_author()) + "\""
        
        # Add VERSION
        node += " VERSION=\"" + escape(self.get_version()) + "\""
        
        # Add FORMAT attribute
        if self.has_format():
            node += " FORMAT=\"" + escape(self.get_format()) + "\""
            
        # Assume default
        else:
            node += " FORMAT=\"2.7\""

        # Close ANNOTATION_DOCUMENT start tag
        node += ">\n"
        
        # Add HEADER node
        node += indent + "<HEADER"

        # Output deprecated MEDIA_FILE attribute with empty value
        node += " MEDIA_FILE=\"\""
        
        # Output TIME_UNITS attribute if there is one
        if self.has_time_units():
            node += " TIME_UNITS=\"" + escape(self.get_time_units()) + "\""
        
        # Output default
        else:
            node += " TIME_UNITS=\"milliseconds\""
        
        # Close HEADER start tag
        node += ">\n"
        
        # Add media descriptors
        for media_descriptor in self.get_media_files():
            
            node += media_descriptor.to_xml(indent=indent)
        
        # Add linked file descriptors
        for linked_file_descriptor in self.get_linked_files():
            
            node += linked_file_descriptor.to_xml(indent=indent)
        
        # Add properties
        for prop in self.properties:
            
            # Add NAME
            node += 2 * indent + "<PROPERTY NAME=\"" + escape(prop) + "\">"

            # Add value
            node += escape(self.get_property(prop))
            
            # Add PROPERTY end tag
            node += "</PROPERTY>\n"
        
        # Add HEADER end tag
        node += indent + "</HEADER>\n"
        
        # ADD TIME_ORDER
        node += self.get_time_order().to_xml(indent=indent)
        
        # Add tiers
        for tier in self.get_tiers():
            
            node += tier.to_xml(indent=indent)
        
        # Add linguistic types
        for linguistic_type in self.get_linguistic_types():
            
            node += linguistic_type.to_xml(indent=indent)

        # Add locales
        for locale in self.get_locales():
            
            node += locale.to_xml(indent=indent)
        
        # Add constraints
        for constraint in self.get_constraints():
            
            node += constraint.to_xml(indent=indent)

        # Add controlled vocabularies
        for controlled_vocabulary in self.get_controlled_vocabularies():
            
            node += controlled_vocabulary.to_xml(indent=indent)

        # Add lexicon references
        for lexicon_reference in self.get_lexicon_references():
            
            node += lexicon_reference.to_xml(indent=indent)
        
        # Add external references
        for external_reference in self.get_external_references():
            
            node += external_reference.to_xml(indent=indent)
        
        # Close ANNOTATION_DOCUMENT node
        node += "</ANNOTATION_DOCUMENT>\n"
        
        # Make sure that the xml can be parsed
        try:

            dom.parseString(node)
            
        except:

            raise RuntimeError("Could not produce well-formed XML from ELANFile object.")
        
        # Return the string representation of the XML node
        return node

    # Getter and setter methods
    def get_url(self):
        return self.url
    
    def get_xml_tree(self):
        return self.xml_tree
    
    def get_author(self):
        return self.author
    
    def get_date(self):
        return self.date
    
    def get_format(self):
        return self.format
    
    def get_version(self):
        return self.version
    
    # Warning: deprecated attribute
    def get_media_file(self):
        return self.media_file
    
    def get_time_units(self):
        return self.time_units
    
    def get_media_files(self):
        return self.media_files
    
    def get_media_files_dict(self):
        return self.media_files_dict
    
    def get_linked_files(self):
        return self.linked_files
    
    def get_linked_files_dict(self):
        return self.linked_files_dict
    
    def get_properties(self):
        return self.properties
    
    def get_property(self, key):
        if key in self.properties:
            return self.properties[key]
        else:
            return None
    
    def get_time_order(self):
        return self.time_order
    
    def get_tiers(self):
        return self.tiers
    
    def get_linguistic_types(self):
        return self.linguistic_types
    
    def get_linguistic_types_dict(self):
        return self.linguistic_types_dict
    
    def get_constraints(self):
        return self.constraints
    
    def get_constraints_dict(self):
        return self.constraints_dict
    
    def get_controlled_vocabularies(self):
        return self.controlled_vocabularies

    def get_controlled_vocabularies_dict(self):
        return self.controlled_vocabularies_dict
    
    def get_locales(self):
        return self.locales
    
    def get_lexicon_references(self):
        return self.lexicon_references
    
    def get_lexicon_references_dict(self):
        return self.lexicon_references_dict
    
    def get_external_references(self):
        return self.external_references
    
    def get_external_references_dict(self):
        return self.external_references_dict
    
    def get_time_slots_dict(self):
        return self.time_slots_dict
    
    def get_annotations_dict(self):
        return self.annotations_dict
    
    # TODO: Implement type checking for setter methods
    def set_url(self, url):
        self.url = url
    
    def set_xml_tree(self, xml_tree):
        self.xml_tree = xml_tree
    
    def set_author(self, author):
        self.author = author
        
    def set_date(self, date):
        self.date = date

    def set_format(self, elan_format):
        self.format = elan_format
    
    def set_version(self, version):
        self.version = version
    
    # Warning: Deprecated attribute
    def set_media_file(self, media_file):
        self.media_file = media_file
    
    # Warning: Should always be milliseconds
    def set_time_units(self, time_units):
        self.time_units = time_units
    
    def set_media_files(self, media_files):
        self.media_files = media_files
    
    def set_media_files_dict(self, media_files_dict):
        self.media_files_dict = media_files_dict
    
    def set_linked_files(self, linked_files):
        self.linked_files = linked_files
    
    def set_linked_files_dict(self, linked_files_dict):
        self.linked_files_dict = linked_files_dict
    
    def set_properties(self, properties):
        self.properties = properties
    
    def set_property(self, prop, value):
        self.properties[prop] = value
    
    def set_time_order(self, time_order):
        self.time_order = time_order
    
    def set_tiers(self, tiers):
        self.tiers = tiers
    
    def set_tiers_dict(self, tiers_dict):
        self.tiers_dict = tiers_dict
    
    def set_linguistic_types(self, linguistic_types):
        self.linguistic_types = linguistic_types
    
    def set_linguistic_types_dict(self, linguistic_types_dict):
        self.linguistic_types_dict = linguistic_types_dict
    
    def set_constraints(self, constraints):
        self.constraints = constraints
    
    def set_constraints_dict(self, constraints_dict):
        self.constraints_dict = constraints_dict
    
    def set_controlled_vocabularies(self, controlled_vocabularies):
        self.controlled_vocabularies = controlled_vocabularies
    
    def set_controlled_vocabularies_dict(self, controlled_vocabularies_dict):
        self.controlled_vocabularies_dict = controlled_vocabularies_dict
    
    def set_locales(self, locales):
        self.locales = locales
    
    def set_lexicon_references(self, lexicon_references):
        self.lexicon_references = lexicon_references
    
    def set_lexicon_references_dict(self, lexicon_references_dict):
        self.lexicon_references_dict = lexicon_references_dict
    
    def set_external_references(self, external_references):
        self.external_references
    
    def set_external_references_dict(self, external_references_dict):
        self.external_references_dict = external_references_dict

    def set_time_slots_dict(self, time_slots_dict):
        self.time_slots_dict = time_slots_dict
    
    def set_annotations_dict(self, annotations_dict):
        self.annotations_dict = annotations_dict
    
    def has_url(self):
        if self.URL is not None:
            return True
        else:
            return False
    
    def has_xml_tree(self):
        if self.xml_tree is not None:
            return True
        else:
            return False

    def has_author(self):
        if self.author is not None:
            return True
        else:
            return False

    def has_date(self):
        if self.date is not None:
            return True
        else:
            return False

    def has_format(self):
        if self.format is not None:
            return True
        else:
            return False

    def has_version(self):
        if self.version is not None:
            return True
        else:
            return False
    
    def has_media_file(self):
        if self.media_file is not None:
            return True
        else:
            return False
    
    def has_time_units(self):
        if self.time_units is not None:
            return True
        else:
            return False

    def has_media_files(self):
        if len(self.media_files) > 0:
            return True
        else:
            return False

    def has_linked_files(self):
        if len(self.linked_files) > 0:
            return True
        else:
            return False

    def has_properties(self):
        if len(self.properties) > 0:
            return True
        else:
            return False

    def has_time_order(self):
        if self.time_order is not None:
            return True
        else:
            return False
    
    def has_tiers(self):
        if len(self.tiers) > 0:
            return True
        else:
            return False
   
    def has_linguistic_types(self):
        if len(self.linguistic_types) > 0:
            return True
        else:
            return False
    
    def has_constraints(self):
        if len(self.constraints) > 0:
            return True
        else:
            return False
    
    def has_controlled_vocabularies(self):
        if len(self.controlled_vocabularies) > 0:
            return True
        else:
            return False
    
    def has_locales(self):
        if len(self.locales) > 0:
            return True
        else:
            return False
        
    def has_lexicon_references(self):
        if len(self.lexicon_references) > 0:
            return True
        else:
            return False

    def has_external_references(self):
        if len(self.external_references) > 0:
            return True
        else:
            return False

    def has_time_slots(self):
        if len(self.time_slots_dict) > 0:
            return True
        else:
            return False

    def has_annotations(self):
        if len(self.annotations_dict) > 0:
            return True
        else:
            return False

    def add_media_file(self, media_file):
        
        # Check type
        if isinstance(media_file, ELANMediaDescriptor):
            self.media_files.append(media_file)
            self.media_files_dict[media_file.get_url()] = media_file
        
        else:
            raise TypeError("Media file to be added has to be of type ELANMediaDescriptor.")

    def add_linked_file(self, linked_file):
        
        # Check type
        if isinstance(linked_file, ELANLinkedFileDescriptor):
            self.linked_files.append(linked_file)
            self.linked_files_dict[linked_file.get_url()] = linked_file
        
        else:
            raise TypeError("Linked file to be added has to be of type ELANLinkedFileDescriptor.")
    
    def add_tier(self, tier):
        
        # Check type
        if isinstance(tier, ELANTier):
            self.tiers.append(tier)
            self.tiers_dict[tier.get_tier_id()] = tier
            
            # Add annotation to annotations_dict
            for annotation in tier:
                self.annotations_dict[annotation.get_annotation_id()] = annotation
        
        else:
            raise TypeError("Tier to be added has to be of type ELANTier.")
    
    def add_linguistic_type(self, linguistic_type):
        
        # Check type
        if isinstance(linguistic_type, ELANLinguisticType):
            self.linguistic_types.append(linguistic_type)
            self.linguistic_types_dict[linguistic_type.get_linguistic_type_id()] = linguistic_type
        
        else:
            raise TypeError("Linguistic type to be added has to be of type ELANLinguisticType.")

    def add_constraint(self, constraint):
        
        # Check type
        if isinstance(constraint, ELANConstraint):
            self.constraints.append(constraint)
            self.constraints_dict[constraint.get_stereotype()] = constraint
        
        else:
            raise TypeError("Constraint to be added has to be of type ELANConstraint.")

    def add_controlled_vocabulary(self, controlled_vocabulary):
        
        # Check type
        if isinstance(controlled_vocabulary, ELANControlledVocabulary):
            self.controlled_vocabularies.append(controlled_vocabulary)
            self.controlled_vocabularies_dict[controlled_vocabulary.get_id()] = controlled_vocabulary
        
        else:
            raise TypeError("Controlled vocabulary to be added has to be of type ELANControlledVocabulary.")
    
    def add_locale(self, locale):
        
        # Check type
        if isinstance(locale, ELANLocale):
            self.locales.append(locale)
        
        else:
            raise TypeError("Locale to be added has to be of type ELANLocale.")

    def add_lexicon_reference(self, lexicon_reference):
        
        # Check type
        if isinstance(lexicon_reference, ELANLexiconReference):
            self.lexicon_references.append(lexicon_reference)
            self.lexicon_references_dict[lexicon_reference.get_id()] = lexicon_reference
        
        else:
            raise TypeError("Lexicon reference to be added has to be of type ELANLexiconReference.")

    def add_external_reference(self, external_reference):
        
        # Check type
        if isinstance(external_reference, ELANExternalReference):
            self.external_references.append(external_reference)
            self.external_references_dict[external_reference.get_id()] = external_reference
        
        else:
            raise TypeError("Lexicon reference to be added has to be of type ELANLexiconReference.")
    
    def add_time_slot(self, time_slot):
        self.time_order.add_time_slot(time_slot)
        self.time_slots_dict[time_slot.get_id()] = time_slot

#         # Get original id of time_slot to be added
#         original_id = time_slot.get_id()
#         time_value = time_slot.get_time_value()
#         
#         # Mapping from old time order to new order
#         time_order_mapping = {}
#         
#         # New time order
#         new_time_order = ELANTimeOrder(self)
#         
#         offset = 0
#         added = False
#         for current_time_slot in self.time_order:
#             
#             # Does the current time slot come after the new time
#             # slot to be inserted?
#             if current_time_slot.get_time_value() > time_value and added is False:
#                 
#                 # Increase offset
#                 offset = 1
#                 
#                 # Set id of new time slot to id of current time slot
#                 new_id = current_time_slot.get_id()
#                 time_slot.set_id(new_id)
#                 
#                 # Add new time slot to new time order
#                 new_time_order.add_time_slot(time_slot)
#                 
#                 # Remember that the new time slot has been added
#                 added = True
# 
#             # Get original id of current time slot
#             old_id = current_time_slot.get_id()
#             
#             # Update annotation id of time_slot
#             if offset > 0:
#                 
#                 match = re.search("^ts(\d+)$", old_id)
#                 if match:
#                     
#                     old_number = int(match.group(1))
#                     new_number = old_number + offset
#                     new_id = "ts" + str(new_number)
#                     
#                     # Create entry in time order mapping
#                     time_order_mapping[old_id] = new_id
#                     
#                     # Change id of current time slot
#                     current_time_slot.set_id(new_id)
#                 
#                 else:
#                     
#                     raise("Could not match time slot id", old_id)
#             
#             else:
#                 
#                 # Leave id of current time slot unchanged
#                 # and enter a corresponding mapping to
#                 # time order mapping
#                 time_order_mapping[old_id] = old_id
#             
#             # Add current time slot to new time order
#             new_time_order.add_time_slot(current_time_slot)
#         
#         # Update annotations
#         for annotation_id in self.annotations_dict:
#             
#             annotation = self.annotations_dict[annotation_id]
# 
#             # Set new start time slot
#             old_start_time_slot = annotation.get_start_time_slot()
#             if old_start_time_slot in time_order_mapping:
#                 
#                 annotation.set_start_time_slot(time_order_mapping[old_start_time_slot])
#                
#             # Set new end time slot
#             old_end_time_slot = annotation.get_end_time_slot()
#             if old_end_time_slot in time_order_mapping:
#                 
#                 annotation.set_end_time_slot(time_order_mapping[old_end_time_slot])
#         
#         # Sort time order
#         self.time_order = sorted(new_time_order)
#         
#         # Update time slots dictionary
#         self.time_slots_dict = {}
#         
#         for current_time_slot in self.time_order:
#             
#             self.time_slots_dict[current_time_slot.get_id()] = current_time_slot
#         
#         # Return new id of new time slot that was inserted
#         return time_slot.get_id()

    def get_media_file_by_url(self, url):
        if url in self.media_files_dict:
            return self.media_files_dict[url]
        else:
            return None

    def get_linked_file_by_url(self, url):
        if url in self.linked_files_dict:
            return self.linked_files_dict[url]
        else:
            return None
    
    def get_file_by_url(self, url):
        if url in self.media_files_dict:
            return self.media_files_dict[url]
        elif url in self.linked_files_dict:
            return self.linked_files_dict[url]
        else:
            return None
    
    def get_time_slot_by_id(self, time_slot_id):
        if time_slot_id in self.time_slots_dict:
            return self.time_slots_dict[time_slot_id]
        else:
            return None

    def get_tier_by_id(self, tier_id):
        if tier_id in self.tiers_dict:
            return self.tiers_dict[tier_id]
        else:
            return None

    def get_annotation_by_id(self, annotation_id):
        if annotation_id in self.annotations_dict:
            return self.annotations_dict[annotation_id]
        else:
            raise KeyError("Unknown annotation ID: " + annotation_id)

    def get_linguistic_type_by_id(self, linguistic_type_id):
        if linguistic_type_id in self.linguistic_types_dict:
            return self.linguistic_types_dict[linguistic_type_id]
        else:
            return None

    def get_constraint_by_stereotype(self, stereotype):
        if stereotype in self.constraints_dict:
            return self.constraints_dict[stereotype]
        else:
            return None

    def get_controlled_vocabulary_by_id(self, cv_id):
        if cv_id in self.cvs_dict:
            return self.cvs_dict[cv_id]
        else:
            return None

    def get_cv_entry_by_value(self, cv_id, value):
        return self.controlled_vocabularies_dict[cv_id].get_cv_entry_by_value(value)
    
    def get_external_reference_by_id(self, ext_ref_id):
        if ext_ref_id in self.ext_refs_dict:
            return self.ext_refs_dict[ext_ref_id]
        else:
            return None

    def get_lexicon_reference_by_id(self, lexicon_ref_id):
        if lexicon_ref_id in self.lexicon_refs_dict:
            return self.lexicon_refs_dict[lexicon_ref_id]
        else:
            return None
